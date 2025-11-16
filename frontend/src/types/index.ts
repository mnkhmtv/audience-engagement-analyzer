export type LectureStatus = 'pending' | 'processing' | 'done' | 'error';

export type UserRole = 'professor' | 'admin';

export interface TimelineHighlight {
  ts_sec: number;
  window_start_sec: number;
  window_end_sec: number;
  engagement_ratio: number;
  attention_ratio: number;
  label: string;
}

export interface AnalysisSummary {
  lecture_id: string;
  frames_analyzed: number;
  faces_total: number;
  avg_attention: number;
  avg_engagement: number;
  score: number;
  emotion_hist: Record<string, number>;
  top_peaks: TimelineHighlight[];
  top_dips: TimelineHighlight[];
  suggestions: string[];
}

export interface AnalysisData {
  lecture_id: string;
  avg_attention: number;
  avg_engagement: number;
  score: number;
  metrics_path: string;
  summary_json: AnalysisSummary | string | null;
  created_at: string;
}

export interface AnalysisResult extends AnalysisData {}

export interface Lecture {
  id: string;
  title: string;
  subject: string | null;
  status: LectureStatus;
  progress: number;
  created_at: string;
  video_tmp_path?: string | null;
  video_url?: string | null;
  error_message?: string | null;
  analysis?: AnalysisResult | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthError {
  detail?: string;
  error?: string;
}
