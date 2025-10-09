'use client';

import { useState } from 'react';
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
  Globe, 
  FileText, 
  Image, 
  Video, 
  MessageSquare,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

const urlIngestSchema = z.object({
  url: z.string().url('Please enter a valid URL'),
  type: z.enum(['web', 'pdf', 'image', 'video']),
  chunkSize: z.number().min(100).max(2000).default(512),
  chunkOverlap: z.number().min(50).max(500).default(76),
});

type UrlIngestFormData = z.infer<typeof urlIngestSchema>;

const modalityOptions = [
  { value: 'web', label: 'Web Page', icon: Globe, description: 'Extract text content from web pages' },
  { value: 'pdf', label: 'PDF Document', icon: FileText, description: 'Process PDF documents' },
  { value: 'image', label: 'Image', icon: Image, description: 'Extract text from images (OCR)' },
  { value: 'video', label: 'Video', icon: Video, description: 'Process video content and transcripts' },
] as const;

export function UrlIngestForm() {
  const router = useRouter();
  const { tenantId, userId } = useUIStore();
  const [jobId, setJobId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<UrlIngestFormData>({
    resolver: zodResolver(urlIngestSchema),
    defaultValues: {
      type: 'web',
      chunkSize: 512,
      chunkOverlap: 76,
    },
  });

  const selectedType = watch('type');

  const ingestMutation = useMutation({
    mutationFn: (data: UrlIngestFormData) => {
      return api.ingestUrl({
        url: data.url,
        type: data.type as any,
        chunk_size: data.chunkSize,
        chunk_overlap: data.chunkOverlap,
      });
    },
    onSuccess: (response) => {
      setJobId(response.job_id);
      toast.success('Ingestion job started successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to start ingestion job');
    },
  });

  const onSubmit = (data: UrlIngestFormData) => {
    ingestMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="h-5 w-5" />
            <span>Ingest from URL</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* URL Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium">URL</label>
              <Input
                {...register('url')}
                placeholder="https://example.com/article"
                className={errors.url ? 'border-red-500' : ''}
              />
              {errors.url && (
                <p className="text-sm text-red-500">{errors.url.message}</p>
              )}
            </div>

            {/* Modality Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Content Type</label>
              <div className="grid gap-3 md:grid-cols-2">
                {modalityOptions.map((option) => (
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
                        <p className="text-sm text-muted-foreground">
                          {option.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

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
                <p className="text-xs text-muted-foreground">
                  Maximum tokens per chunk (100-2000)
                </p>
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
                <p className="text-xs text-muted-foreground">
                  Tokens to overlap between chunks (50-500)
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex items-center space-x-4">
              <Button
                type="submit"
                disabled={ingestMutation.isPending}
                className="flex-1"
              >
                {ingestMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Starting Ingestion...
                  </>
                ) : (
                  <>
                    <Globe className="h-4 w-4 mr-2" />
                    Start Ingestion
                  </>
                )}
              </Button>
              
              {jobId && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push(`/processing?job_id=${jobId}`)}
                >
                  View Job
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
              Supported formats: HTML pages, PDFs, images (JPEG, PNG), videos (MP4, WebM)
            </p>
          </div>
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Large documents are automatically chunked for better retrieval
            </p>
          </div>
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              Processing time depends on content size and complexity
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
