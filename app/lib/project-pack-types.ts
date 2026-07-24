export interface ProjectPackSummary {
  files: number;
  sizeBytes: number;
  categories: number;
  csvFiles: number;
  sqlFiles: number;
  guideFiles: number;
  testFiles: number;
}

export interface ProjectPackCategory {
  id: string;
  label: string;
  description: string;
  count: number;
  sizeBytes: number;
}

export interface ProjectPackFile {
  path: string;
  name: string;
  title: string;
  extension: string;
  kind: string;
  category: string;
  sizeBytes: number;
  sha256: string;
  featuredOrder: number | null;
  featuredTitle: string;
  description: string;
}

export interface ProjectPackIndex {
  contractVersion: string;
  title: string;
  sourceRepository: string;
  pagesUrl: string;
  sourceCommit: string;
  policy: string;
  summary: ProjectPackSummary;
  categories: ProjectPackCategory[];
  files: ProjectPackFile[];
}
