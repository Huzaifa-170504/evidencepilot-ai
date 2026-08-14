export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.15"
  }
  public: {
    Tables: {
      agent_events: {
        Row: {
          agent_name: string
          created_at: string
          duration_ms: number
          id: number
          owner_id: string
          project_id: string
          run_id: string
          safe_metadata: Json
          sequence: number
          status: string
          summary: string
        }
        Insert: {
          agent_name: string
          created_at?: string
          duration_ms?: number
          id?: never
          owner_id: string
          project_id: string
          run_id: string
          safe_metadata?: Json
          sequence: number
          status: string
          summary: string
        }
        Update: {
          agent_name?: string
          created_at?: string
          duration_ms?: number
          id?: never
          owner_id?: string
          project_id?: string
          run_id?: string
          safe_metadata?: Json
          sequence?: number
          status?: string
          summary?: string
        }
        Relationships: [
          {
            foreignKeyName: "agent_events_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "agent_events_run_id_fkey"
            columns: ["run_id"]
            isOneToOne: false
            referencedRelation: "research_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      agent_tasks: {
        Row: {
          agent_name: string
          completed_at: string | null
          created_at: string
          dependencies: Json
          error: string | null
          id: string
          input: Json
          objective: string
          output: Json
          owner_id: string
          project_id: string
          run_id: string
          started_at: string | null
          status: string
          task_key: string
          title: string
        }
        Insert: {
          agent_name: string
          completed_at?: string | null
          created_at?: string
          dependencies?: Json
          error?: string | null
          id?: string
          input?: Json
          objective: string
          output?: Json
          owner_id: string
          project_id: string
          run_id: string
          started_at?: string | null
          status: string
          task_key: string
          title: string
        }
        Update: {
          agent_name?: string
          completed_at?: string | null
          created_at?: string
          dependencies?: Json
          error?: string | null
          id?: string
          input?: Json
          objective?: string
          output?: Json
          owner_id?: string
          project_id?: string
          run_id?: string
          started_at?: string | null
          status?: string
          task_key?: string
          title?: string
        }
        Relationships: [
          {
            foreignKeyName: "agent_tasks_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "agent_tasks_run_id_fkey"
            columns: ["run_id"]
            isOneToOne: false
            referencedRelation: "research_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      claim_evidence: {
        Row: {
          claim_id: string
          created_at: string
          excerpt: string | null
          id: string
          owner_id: string
          project_id: string
          relationship: string
          run_id: string
          source_id: string
        }
        Insert: {
          claim_id: string
          created_at?: string
          excerpt?: string | null
          id?: string
          owner_id: string
          project_id: string
          relationship: string
          run_id: string
          source_id: string
        }
        Update: {
          claim_id?: string
          created_at?: string
          excerpt?: string | null
          id?: string
          owner_id?: string
          project_id?: string
          relationship?: string
          run_id?: string
          source_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "claim_evidence_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "claim_evidence_run_id_claim_id_fkey"
            columns: ["run_id", "claim_id"]
            isOneToOne: false
            referencedRelation: "claims"
            referencedColumns: ["run_id", "id"]
          },
          {
            foreignKeyName: "claim_evidence_run_id_source_id_fkey"
            columns: ["run_id", "source_id"]
            isOneToOne: false
            referencedRelation: "sources"
            referencedColumns: ["run_id", "id"]
          },
        ]
      }
      claims: {
        Row: {
          claim_text: string
          confidence: number
          created_at: string
          id: string
          owner_id: string
          project_id: string
          rationale: string | null
          run_id: string
          source_ids: string[]
          verdict: string
        }
        Insert: {
          claim_text: string
          confidence: number
          created_at?: string
          id: string
          owner_id: string
          project_id: string
          rationale?: string | null
          run_id: string
          source_ids?: string[]
          verdict: string
        }
        Update: {
          claim_text?: string
          confidence?: number
          created_at?: string
          id?: string
          owner_id?: string
          project_id?: string
          rationale?: string | null
          run_id?: string
          source_ids?: string[]
          verdict?: string
        }
        Relationships: [
          {
            foreignKeyName: "claims_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "claims_run_id_fkey"
            columns: ["run_id"]
            isOneToOne: false
            referencedRelation: "research_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      document_chunks: {
        Row: {
          char_end: number
          char_start: number
          chunk_index: number
          content: string
          content_tsv: unknown
          created_at: string
          document_id: string
          embedding: string | null
          id: string
          metadata: Json
          owner_id: string
          page_number: number
          project_id: string
          section_heading: string | null
        }
        Insert: {
          char_end?: number
          char_start?: number
          chunk_index: number
          content: string
          content_tsv?: unknown
          created_at?: string
          document_id: string
          embedding?: string | null
          id?: string
          metadata?: Json
          owner_id: string
          page_number: number
          project_id: string
          section_heading?: string | null
        }
        Update: {
          char_end?: number
          char_start?: number
          chunk_index?: number
          content?: string
          content_tsv?: unknown
          created_at?: string
          document_id?: string
          embedding?: string | null
          id?: string
          metadata?: Json
          owner_id?: string
          page_number?: number
          project_id?: string
          section_heading?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "document_chunks_document_id_fkey"
            columns: ["document_id"]
            isOneToOne: false
            referencedRelation: "documents"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "document_chunks_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      documents: {
        Row: {
          checksum_sha256: string | null
          created_at: string
          filename: string
          id: string
          mime_type: string
          owner_id: string
          page_count: number | null
          processing_error: string | null
          project_id: string
          size_bytes: number
          status: string
          storage_path: string
          updated_at: string
        }
        Insert: {
          checksum_sha256?: string | null
          created_at?: string
          filename: string
          id?: string
          mime_type?: string
          owner_id: string
          page_count?: number | null
          processing_error?: string | null
          project_id: string
          size_bytes: number
          status?: string
          storage_path: string
          updated_at?: string
        }
        Update: {
          checksum_sha256?: string | null
          created_at?: string
          filename?: string
          id?: string
          mime_type?: string
          owner_id?: string
          page_count?: number | null
          processing_error?: string | null
          project_id?: string
          size_bytes?: number
          status?: string
          storage_path?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "documents_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      feedback: {
        Row: {
          comments: string | null
          created_at: string
          id: string
          labels: Json
          owner_id: string
          project_id: string
          rating: number | null
          run_id: string
        }
        Insert: {
          comments?: string | null
          created_at?: string
          id?: string
          labels?: Json
          owner_id: string
          project_id: string
          rating?: number | null
          run_id: string
        }
        Update: {
          comments?: string | null
          created_at?: string
          id?: string
          labels?: Json
          owner_id?: string
          project_id?: string
          rating?: number | null
          run_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "feedback_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "feedback_run_id_fkey"
            columns: ["run_id"]
            isOneToOne: false
            referencedRelation: "research_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      findings: {
        Row: {
          agent_name: string
          created_at: string
          id: string
          owner_id: string
          project_id: string
          run_id: string
          source_ids: string[]
          summary: string
          uncertainty: string | null
        }
        Insert: {
          agent_name: string
          created_at?: string
          id?: string
          owner_id: string
          project_id: string
          run_id: string
          source_ids?: string[]
          summary: string
          uncertainty?: string | null
        }
        Update: {
          agent_name?: string
          created_at?: string
          id?: string
          owner_id?: string
          project_id?: string
          run_id?: string
          source_ids?: string[]
          summary?: string
          uncertainty?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "findings_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "findings_run_id_fkey"
            columns: ["run_id"]
            isOneToOne: false
            referencedRelation: "research_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      jobs: {
        Row: {
          attempt_count: number
          available_at: string
          checkpoint: Json
          created_at: string
          entity_id: string
          error: string | null
          id: string
          job_type: string
          max_attempts: number
          owner_id: string
          project_id: string
          status: string
          updated_at: string
        }
        Insert: {
          attempt_count?: number
          available_at?: string
          checkpoint?: Json
          created_at?: string
          entity_id: string
          error?: string | null
          id?: string
          job_type: string
          max_attempts?: number
          owner_id: string
          project_id: string
          status?: string
          updated_at?: string
        }
        Update: {
          attempt_count?: number
          available_at?: string
          checkpoint?: Json
          created_at?: string
          entity_id?: string
          error?: string | null
          id?: string
          job_type?: string
          max_attempts?: number
          owner_id?: string
          project_id?: string
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "jobs_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      memories: {
        Row: {
          content: string
          created_at: string
          embedding: string | null
          enabled: boolean
          id: string
          memory_type: string
          owner_id: string
          project_id: string | null
          title: string
          updated_at: string
        }
        Insert: {
          content: string
          created_at?: string
          embedding?: string | null
          enabled?: boolean
          id?: string
          memory_type: string
          owner_id: string
          project_id?: string | null
          title: string
          updated_at?: string
        }
        Update: {
          content?: string
          created_at?: string
          embedding?: string | null
          enabled?: boolean
          id?: string
          memory_type?: string
          owner_id?: string
          project_id?: string | null
          title?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "memories_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      messages: {
        Row: {
          content: string
          created_at: string
          id: string
          owner_id: string
          project_id: string
          role: string
        }
        Insert: {
          content: string
          created_at?: string
          id?: string
          owner_id: string
          project_id: string
          role: string
        }
        Update: {
          content?: string
          created_at?: string
          id?: string
          owner_id?: string
          project_id?: string
          role?: string
        }
        Relationships: [
          {
            foreignKeyName: "messages_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          created_at: string
          display_name: string | null
          id: string
          memory_enabled: boolean
          report_preferences: Json
          updated_at: string
        }
        Insert: {
          created_at?: string
          display_name?: string | null
          id: string
          memory_enabled?: boolean
          report_preferences?: Json
          updated_at?: string
        }
        Update: {
          created_at?: string
          display_name?: string | null
          id?: string
          memory_enabled?: boolean
          report_preferences?: Json
          updated_at?: string
        }
        Relationships: []
      }
      project_members: {
        Row: {
          created_at: string
          project_id: string
          role: string
          user_id: string
        }
        Insert: {
          created_at?: string
          project_id: string
          role?: string
          user_id: string
        }
        Update: {
          created_at?: string
          project_id?: string
          role?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "project_members_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      projects: {
        Row: {
          created_at: string
          description: string
          id: string
          is_public_demo: boolean
          name: string
          owner_id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          description?: string
          id?: string
          is_public_demo?: boolean
          name: string
          owner_id: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          description?: string
          id?: string
          is_public_demo?: boolean
          name?: string
          owner_id?: string
          updated_at?: string
        }
        Relationships: []
      }
      research_runs: {
        Row: {
          budgets: Json
          completed_at: string | null
          correlation_id: string | null
          created_at: string
          depth: string
          final_report_markdown: string | null
          id: string
          metrics: Json
          owner_id: string
          plan: Json
          project_id: string
          question: string
          snapshot: Json
          started_at: string | null
          status: string
          updated_at: string
        }
        Insert: {
          budgets?: Json
          completed_at?: string | null
          correlation_id?: string | null
          created_at?: string
          depth?: string
          final_report_markdown?: string | null
          id: string
          metrics?: Json
          owner_id: string
          plan?: Json
          project_id: string
          question: string
          snapshot?: Json
          started_at?: string | null
          status?: string
          updated_at?: string
        }
        Update: {
          budgets?: Json
          completed_at?: string | null
          correlation_id?: string | null
          created_at?: string
          depth?: string
          final_report_markdown?: string | null
          id?: string
          metrics?: Json
          owner_id?: string
          plan?: Json
          project_id?: string
          question?: string
          snapshot?: Json
          started_at?: string | null
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "research_runs_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      sources: {
        Row: {
          accessed_at: string
          arxiv_id: string | null
          authors: Json
          canonical_url: string | null
          document_id: string | null
          doi: string | null
          excerpt: string | null
          id: string
          metadata: Json
          owner_id: string
          page_number: number | null
          project_id: string
          publication_year: number | null
          publisher: string | null
          run_id: string
          source_type: string
          title: string
          url: string | null
        }
        Insert: {
          accessed_at?: string
          arxiv_id?: string | null
          authors?: Json
          canonical_url?: string | null
          document_id?: string | null
          doi?: string | null
          excerpt?: string | null
          id: string
          metadata?: Json
          owner_id: string
          page_number?: number | null
          project_id: string
          publication_year?: number | null
          publisher?: string | null
          run_id: string
          source_type: string
          title: string
          url?: string | null
        }
        Update: {
          accessed_at?: string
          arxiv_id?: string | null
          authors?: Json
          canonical_url?: string | null
          document_id?: string | null
          doi?: string | null
          excerpt?: string | null
          id?: string
          metadata?: Json
          owner_id?: string
          page_number?: number | null
          project_id?: string
          publication_year?: number | null
          publisher?: string | null
          run_id?: string
          source_type?: string
          title?: string
          url?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "sources_document_id_fkey"
            columns: ["document_id"]
            isOneToOne: false
            referencedRelation: "documents"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "sources_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "sources_run_id_fkey"
            columns: ["run_id"]
            isOneToOne: false
            referencedRelation: "research_runs"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      hybrid_search_document_chunks: {
        Args: {
          match_count?: number
          query_embedding: string
          query_text: string
          target_project_id: string
        }
        Returns: {
          content: string
          document_id: string
          filename: string
          id: string
          page_number: number
          score: number
          section_heading: string
        }[]
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const

