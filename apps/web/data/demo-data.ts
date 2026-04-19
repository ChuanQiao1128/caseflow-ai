export type MatterDemo = {
  id: string;
  title: string;
  organisation: string;
  type: string;
  status: string;
  settlementDate: string;
  client: string;
  lastUpdated: string;
  reference: string | null;
};

export type WorkflowStep = {
  name: string;
  summary: string;
  state: 'done' | 'active' | 'blocked';
};

export type EvidenceCitation = {
  label: string;
  citation: string;
  note: string;
};

export type ExtractionField = {
  name: string;
  value: string;
  citation: string;
  confidence: string;
};

export type ChecklistItem = {
  name: string;
  status: 'pass' | 'unclear';
  reason: string;
  citation: string;
};

export type ReviewDecisionDemo = {
  summary: string;
  status: 'needs_human_review' | 'ready_for_review' | 'insufficient_evidence';
  disclaimer: string;
};

export type ApprovalQueueItemDemo = {
  id: string;
  matterId: string;
  subject: string;
  context: string;
  reason: string;
  status: 'pending' | 'needs_changes' | 'approved';
  updatedAt: string;
  reviewerNotes?: string | null;
};

export type DocumentDemo = {
  id: string;
  name: string;
  pages: string;
  tag: string;
};

export type AuditLogDemo = {
  id: string;
  action: string;
  entityType: string;
  entityId: string;
  details: string;
  createdAt: string;
};

export const demoMatter: MatterDemo = {
  id: 'matter-001',
  title: 'Pukekohe Purchase for the Ngata Family',
  organisation: 'Kauri Coast Legal',
  type: 'Individual buyer + mortgage',
  status: 'Needs human review',
  settlementDate: '14 May 2026',
  client: 'Ngata Family',
  lastUpdated: 'Updated 8 minutes ago',
  reference: 'DEMO-001'
};

export const demoWorkflowSteps: WorkflowStep[] = [
  {
    name: 'Ingest documents',
    summary: 'Synthetic settlement pack loaded and classified.',
    state: 'done'
  },
  {
    name: 'Extract key facts',
    summary: 'Purchase price, lender, and settlement date captured.',
    state: 'done'
  },
  {
    name: 'Run checklist review',
    summary: 'Proof of address and insurance timing need review.',
    state: 'active'
  },
  {
    name: 'Queue for approval',
    summary: 'Draft follow-up email is waiting for a human decision.',
    state: 'blocked'
  }
];

export const demoEvidence: EvidenceCitation[] = [
  {
    label: 'Purchase agreement date',
    citation: 'Sale & Purchase Agreement · Page 2',
    note: 'Shows the transaction timeline used for the settlement plan.'
  },
  {
    label: 'Bank mortgage lender',
    citation: 'Loan Offer Letter · Page 4',
    note: 'Confirms lender details for the review summary.'
  },
  {
    label: 'Missing proof of address',
    citation: 'Checklist review · needs_human_review',
    note: 'No current proof of address was found in the synthetic pack.'
  }
];

export const demoFields: ExtractionField[] = [
  {
    name: 'Settlement date',
    value: '14 May 2026',
    citation: 'Sale & Purchase Agreement · Page 2',
    confidence: '0.96'
  },
  {
    name: 'Purchaser type',
    value: 'Individual buyer with mortgage',
    citation: 'Matter summary · Page 1',
    confidence: '0.91'
  },
  {
    name: 'Lender',
    value: 'Aotearoa Bank',
    citation: 'Loan Offer Letter · Page 4',
    confidence: '0.93'
  }
];

export const demoChecklist: ChecklistItem[] = [
  {
    name: 'Proof of address',
    status: 'unclear',
    reason: 'No current utility bill or bank statement found.',
    citation: 'Compliance pack · Page 8'
  },
  {
    name: 'Insurance timing',
    status: 'unclear',
    reason: 'Policy start date appears to be after settlement.',
    citation: 'Insurance certificate · Page 6'
  },
  {
    name: 'Mortgage evidence',
    status: 'pass',
    reason: 'Loan offer and lender details are present.',
    citation: 'Loan Offer Letter · Page 4'
  }
];

export const demoReview: ReviewDecisionDemo = {
  summary: 'Ready for human review. The matter is bounded and not legal advice.',
  status: 'ready_for_review',
  disclaimer:
    'This review is a bounded human review aid, not legal advice or legal approval. It highlights evidence for manual review.'
};

export const demoQueueItems: ApprovalQueueItemDemo[] = [
  {
    id: 'aq-001',
    matterId: demoMatter.id,
    subject: 'Follow-up email: missing proof of address',
    context: 'Draft email to request a current proof of address for each buyer.',
    reason: 'No recent utility bill or bank statement was found in the synthetic pack.',
    status: 'pending',
    updatedAt: 'Updated 5 minutes ago',
    reviewerNotes: null
  },
  {
    id: 'aq-002',
    matterId: demoMatter.id,
    subject: 'Follow-up email: insurance timing',
    context: 'Draft email to confirm cover begins on or before settlement.',
    reason: 'The policy start date is after settlement in this demo dataset.',
    status: 'needs_changes',
    updatedAt: 'Updated 12 minutes ago',
    reviewerNotes: 'Tighten the wording before sending.'
  },
  {
    id: 'aq-003',
    matterId: demoMatter.id,
    subject: 'Follow-up email: gifted funds ID',
    context: 'Draft email to request donor identification for gifted funds.',
    reason: 'The source-of-funds pack is missing donor identification details.',
    status: 'pending',
    updatedAt: 'Updated 20 minutes ago',
    reviewerNotes: null
  }
];

export const demoDocuments: DocumentDemo[] = [
  { id: 'doc-1', name: 'Sale & Purchase Agreement', pages: '8 pages', tag: 'Contract' },
  { id: 'doc-2', name: 'Loan Offer Letter', pages: '6 pages', tag: 'Mortgage' },
  { id: 'doc-3', name: 'Compliance pack', pages: '10 pages', tag: 'CDD' }
];

export const demoAuditLogs: AuditLogDemo[] = [
  {
    id: 'log-1',
    action: 'matter.created',
    entityType: 'matter',
    entityId: demoMatter.id,
    details: 'Matter created for synthetic demo flow.',
    createdAt: 'Updated 2 hours ago'
  },
  {
    id: 'log-2',
    action: 'document.registered',
    entityType: 'document',
    entityId: 'doc-1',
    details: 'Registered sale and purchase agreement for review.',
    createdAt: 'Updated 1 hour ago'
  },
  {
    id: 'log-3',
    action: 'approval_queue.created',
    entityType: 'approval_queue_item',
    entityId: 'aq-001',
    details: 'Created follow-up email draft requiring human approval.',
    createdAt: 'Updated 5 minutes ago'
  }
];

export const demoMetrics = [
  { label: 'Documents', value: '3', hint: 'Synthetic pack registered for this matter' },
  { label: 'Extracted facts', value: '3', hint: 'Cited fields ready for review' },
  { label: 'Open queue items', value: '2', hint: 'Waiting for human approval' },
  { label: 'Evidence confidence', value: 'High', hint: 'Bounded workflow, no final legal advice' }
];
