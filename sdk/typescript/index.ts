/**
 * Engram TypeScript SDK
 * Universal Memory Layer for LLMs
 */

export interface MemoryResponse {
  id: string;
  tenant_id: string;
  user_id: string;
  text: string;
  metadata: Record<string, any>;
  modality: string;
  source_uri?: string;
  importance: number;
  created_at: string;
}

export interface ChatResponse {
  reply: string;
  memories_used: Array<Record<string, any>>;
  trace_id: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  description?: string;
}

export interface GraphEdge {
  id: string;
  src_id: string;
  dst_id: string;
  relation: string;
  weight: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface JobResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface RetrievalHints {
  modalities?: string[];
  k?: number;
  importance_min?: number;
}

export interface ChatMessage {
  role: string;
  content: string;
}

export class EngramClient {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;

  constructor(
    apiKey: string,
    baseUrl: string = "http://localhost:8000",
    timeout: number = 30000
  ) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.timeout = timeout;
  }

  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    params?: Record<string, any>
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}/v1${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.apiKey}`,
      "Content-Type": "application/json",
    };

    const config: RequestInit = {
      method,
      headers,
      signal: AbortSignal.timeout(this.timeout),
    };

    if (data && method !== "GET") {
      config.body = JSON.stringify(data);
    }

    const response = await fetch(url.toString(), config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async upsert(
    tenantId: string,
    userId: string,
    text: string,
    metadata?: Record<string, any>,
    importance: number = 0.5
  ): Promise<MemoryResponse> {
    const data = {
      tenant_id: tenantId,
      user_id: userId,
      text,
      metadata: metadata || {},
      importance,
    };

    return this.request<MemoryResponse>("POST", "/memories/upsert", data);
  }

  async ingestUrl(
    tenantId: string,
    userId: string,
    url: string,
    contentType: string = "web"
  ): Promise<JobResponse> {
    const data = {
      url,
      type: contentType,
    };

    return this.request<JobResponse>("POST", "/ingest/url", data);
  }

  async ingestChat(
    tenantId: string,
    userId: string,
    platform: string,
    messages: Array<Record<string, any>>,
    metadata?: Record<string, any>
  ): Promise<JobResponse> {
    const data = {
      platform,
      items: messages,
      metadata: metadata || {},
    };

    return this.request<JobResponse>("POST", "/ingest/chat", data);
  }

  async retrieve(
    tenantId: string,
    userId: string,
    query: string,
    topK: number = 10,
    modalities?: string[]
  ): Promise<MemoryResponse[]> {
    const data = {
      tenant_id: tenantId,
      user_id: userId,
      query,
      top_k: topK,
      modalities,
    };

    const response = await this.request<{ memories: MemoryResponse[] }>(
      "POST",
      "/memories/retrieve",
      data
    );

    return response.memories;
  }

  async chat(
    tenantId: string,
    userId: string,
    messages: ChatMessage[],
    retrievalHints?: RetrievalHints
  ): Promise<ChatResponse> {
    const data = {
      tenant_id: tenantId,
      user_id: userId,
      messages,
      retrieval_hints: retrievalHints,
    };

    return this.request<ChatResponse>("POST", "/chat", data);
  }

  async routerComplete(
    tenantId: string,
    userId: string,
    messages: ChatMessage[],
    provider?: string,
    model?: string,
    retrievalHints?: RetrievalHints
  ): Promise<Record<string, any>> {
    const data = {
      provider,
      model,
      messages,
      retrieval_hints: retrievalHints,
    };

    return this.request<Record<string, any>>("POST", "/router/complete", data);
  }

  async graphSubgraph(
    tenantId: string,
    userId: string,
    seedLabel: string,
    radius: number = 2
  ): Promise<GraphResponse> {
    const params = {
      tenant_id: tenantId,
      user_id: userId,
      seed_label: seedLabel,
      radius: radius.toString(),
    };

    return this.request<GraphResponse>("GET", "/graph/subgraph", undefined, params);
  }

  async graphSearch(
    tenantId: string,
    userId: string,
    entity: string
  ): Promise<GraphNode[]> {
    const params = {
      tenant_id: tenantId,
      user_id: userId,
      entity,
    };

    const response = await this.request<{ nodes: GraphNode[] }>(
      "GET",
      "/graph/search",
      undefined,
      params
    );

    return response.nodes;
  }

  async listMemories(
    tenantId: string,
    userId: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<MemoryResponse[]> {
    const params = {
      tenant_id: tenantId,
      user_id: userId,
      limit: limit.toString(),
      offset: offset.toString(),
    };

    const response = await this.request<{ memories: MemoryResponse[] }>(
      "GET",
      "/admin/memories",
      undefined,
      params
    );

    return response.memories;
  }

  async processingStatus(jobId: string): Promise<Record<string, any>> {
    const params = { job_id: jobId };
    return this.request<Record<string, any>>(
      "GET",
      "/processing/status",
      undefined,
      params
    );
  }
}

// Export for both CommonJS and ES modules
export default EngramClient;

// Node.js compatibility
if (typeof module !== "undefined" && module.exports) {
  module.exports = EngramClient;
  module.exports.default = EngramClient;
}
