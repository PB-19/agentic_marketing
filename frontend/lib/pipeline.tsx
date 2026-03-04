"use client";
import { createContext, useContext, useState, ReactNode } from "react";

// Mirrors backend Pydantic shapes (minimal)
export interface Competitor {
  name: string; strengths: string; weaknesses: string; positioning: string;
}
export interface ResearchResult {
  domain_primary: string;
  domain_secondary: string[];
  novelty_verdict: string;
  differentiating_aspects: string[];
  competitors: Competitor[];
  marketing_implications: string[];
}
export interface TrendBrief {
  trending_styles: { format: string; visual_style: string; tone: string };
  top_influencers: { handle: string; niche: string; style: string; why_relevant: string }[];
  caption_patterns: { structure: string; avg_length: string; emoji_usage: string; cta_style: string };
  hashtag_strategy: { volume_mix: string; top_hashtags: string[] };
  content_generation_brief: string;
}
export interface GeneratedPost {
  image_url: string;
  caption: string;
  hashtags: string[];
}
export interface DeployResult {
  html: string; gcs_url: string; tiny_url: string; iteration: number; notes?: string;
}

interface PipelineState {
  idea: string;
  research: ResearchResult | null;
  deploy: DeployResult | null;
  trendBrief: TrendBrief | null;
  posts: GeneratedPost[];
  setIdea: (v: string) => void;
  setResearch: (v: ResearchResult) => void;
  setDeploy: (v: DeployResult) => void;
  setTrendBrief: (v: TrendBrief) => void;
  setPosts: (v: GeneratedPost[]) => void;
  reset: () => void;
}

const Ctx = createContext<PipelineState | null>(null);

export function PipelineProvider({ children }: { children: ReactNode }) {
  const [idea, setIdea] = useState("");
  const [research, setResearch] = useState<ResearchResult | null>(null);
  const [deploy, setDeploy] = useState<DeployResult | null>(null);
  const [trendBrief, setTrendBrief] = useState<TrendBrief | null>(null);
  const [posts, setPosts] = useState<GeneratedPost[]>([]);

  const reset = () => {
    setIdea(""); setResearch(null); setDeploy(null);
    setTrendBrief(null); setPosts([]);
  };

  return (
    <Ctx.Provider value={{ idea, research, deploy, trendBrief, posts, setIdea, setResearch, setDeploy, setTrendBrief, setPosts, reset }}>
      {children}
    </Ctx.Provider>
  );
}

export function usePipeline() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("usePipeline must be inside PipelineProvider");
  return ctx;
}
