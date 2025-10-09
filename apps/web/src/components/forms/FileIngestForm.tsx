'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useUIStore } from '@/store/ui';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  File, 
  Image, 
  Video, 
  FileText,
  Loader2,
  CheckCircle,
  AlertCircle,
  X,
  FileIcon
} from 'lucide-react';
import { toast } from 'sonner';
import { formatFileSize, isImageFile, isVideoFile, isPdfFile } from '@/lib/utils';

const fileIngestSchema = z.object({
  type: z.enum(['pdf', 'image', 'video', 'text']),
  chunkSize: z.number().min(100).max(2000).default(512),
  chunkOverlap: z.number().min(50).max(500).default(76),
});

type FileIngestFormData = z.infer<typeof fileIngestSchema>;

interface FileWithPreview extends File {
  preview?: string;
}

export function FileIngestForm() {
  const router = useRouter();
  const { tenantId, userId } = useUIStore();
  const [uploadedFiles, setUploadedFiles] = useState<FileWithPreview[]>([]);
  const [jobIds, setJobIds] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FileIngestFormData>({
    resolver: zodResolver(fileIngestSchema),
    defaultValues: {
      type: 'pdf',
      chunkSize: 512,
      chunkOverlap: 76,
    },
  });

  const selectedType = watch('type');

  const ingestMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', selectedType);
      formData.append('chunk_size', watch('chunkSize').toString());
      formData.append('chunk_overlap', watch('chunkOverlap').toString());

      return api.ingestFile(formData);
    },
    onSuccess: (response, file) => {
      setJobIds(prev => [...prev, response.job_id]);
      toast.success(`File ${file.name} uploaded successfully`);
    },
    onError: (error: any, file) => {
      toast.error(`Failed to upload ${file.name}: ${error.message}`);
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      ...file,
      preview: isImageFile(file.name) ? URL.createObjectURL(file) : undefined,
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'video/*': ['.mp4', '.webm', '.avi', '.mov'],
      'text/*': ['.txt', '.md', '.csv'],
    },
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const removeFile = (index: number) => {
    const file = uploadedFiles[index];
    if (file.preview) {
      URL.revokeObjectURL(file.preview);
    }
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const getFileIcon = (file: File) => {
    if (isPdfFile(file.name)) return FileText;
    if (isImageFile(file.name)) return Image;
    if (isVideoFile(file.name)) return Video;
    return FileIcon;
  };

  const onSubmit = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('Please select at least one file to upload');
      return;
    }

    // Process all files
    for (const file of uploadedFiles) {
      ingestMutation.mutate(file);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Upload Files</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* File Type Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium">File Type</label>
              <div className="grid gap-3 md:grid-cols-2">
                {[
                  { value: 'pdf', label: 'PDF Documents', icon: FileText },
                  { value: 'image', label: 'Images', icon: Image },
                  { value: 'video', label: 'Videos', icon: Video },
                  { value: 'text', label: 'Text Files', icon: File },
                ].map((option) => (
                  <div
                    key={option.value}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedType === option.value
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                    onClick={() => setValue('type', option.value as any)}
                  >
                    <div className="flex items-center space-x-3">
                      <option.icon className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{option.label}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* File Upload Area */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Files</label>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                {isDragActive ? (
                  <p className="text-lg">Drop the files here...</p>
                ) : (
                  <div>
                    <p className="text-lg mb-2">
                      Drag & drop files here, or click to select
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Supports PDF, images, videos, and text files (max 100MB each)
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-3">
                <label className="text-sm font-medium">Selected Files</label>
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => {
                    const FileIcon = getFileIcon(file);
                    return (
                      <div
                        key={index}
                        className="flex items-center space-x-3 p-3 border rounded-lg"
                      >
                        <FileIcon className="h-5 w-5 text-muted-foreground" />
                        {file.preview && (
                          <img
                            src={file.preview}
                            alt={file.name}
                            className="h-10 w-10 rounded object-cover"
                          />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{file.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {formatFileSize(file.size)}
                          </p>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeFile(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Chunking Options */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Chunk Size</label>
                <Input
                  {...register('chunkSize', { valueAsNumber: true })}
                  type="number"
                  min={100}
                  max={2000}
                  className={errors.chunkSize ? 'border-red-500' : ''}
                />
                {errors.chunkSize && (
                  <p className="text-sm text-red-500">
                    {errors.chunkSize.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Chunk Overlap</label>
                <Input
                  {...register('chunkOverlap', { valueAsNumber: true })}
                  type="number"
                  min={50}
                  max={500}
                  className={errors.chunkOverlap ? 'border-red-500' : ''}
                />
                {errors.chunkOverlap && (
                  <p className="text-sm text-red-500">
                    {errors.chunkOverlap.message}
                  </p>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex items-center space-x-4">
              <Button
                type="submit"
                disabled={ingestMutation.isPending || uploadedFiles.length === 0}
                className="flex-1"
              >
                {ingestMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading Files...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload {uploadedFiles.length} File{uploadedFiles.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
              
              {jobIds.length > 0 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push('/processing')}
                >
                  View Jobs ({jobIds.length})
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Tips</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Supported formats: PDF, images (PNG, JPG, GIF, WebP), videos (MP4, WebM, AVI, MOV), text files
            </p>
          </div>
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              You can upload multiple files at once for batch processing
            </p>
          </div>
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Large files may take longer to process. Progress will be shown in the jobs section
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
