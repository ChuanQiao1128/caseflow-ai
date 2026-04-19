export type MatterDemo = {
  title: string;
  organisation: string;
  type: string;
  status: string;
  settlementDate: string;
};

export type WorkflowStep = {
  name: string;
  summary: string;
  state: 'done' | 'active' | 'blocked';
};

export type ApprovalQueueItemDemo = {
  id: string;
  matterId: string;
  subject: string;
  context: string;
  reason: string;
  status: 'pending' | 'needs_changes' | 'approved';
  updatedAt: string;
};

export const demoMatter: MatterDemo = {
  title: 'Pukekohe Purchase for the Ngata Family',
  organisation: 'Kauri Coast Legal',
  type: 'Individual buyer + mortgage',
  status: 'Needs human review',
  settlementDate: '14 May 2026'
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

export const demoQueueItems: ApprovalQueueItemDemo[] = [
  {
    id: 'aq-001',
    matterId: 'case-001',
    subject: 'Follow-up email: missing proof of address',
    context: 'Draft email to request a current proof of address for each buyer.',
    reason: 'No recent utility bill or bank statement was found in the synthetic pack.',
    status: 'pending',
    updatedAt: 'Updated 5 minutes ago'
  },
  {
    id: 'aq-002',
    matterId: 'case-001',
    subject: 'Follow-up email: insurance timing',
    context: 'Draft email to confirm cover begins on or before settlement.',
    reason: 'The policy start date is after settlement in this demo dataset.',
    status: 'needs_changes',
    updatedAt: 'Updated 12 minutes ago'
  },
  {
    id: 'aq-003',
    matterId: 'case-001',
    subject: 'Follow-up email: gifted funds ID',
    context: 'Draft email to request donor identification for gifted funds.',
    reason: 'The source-of-funds pack is missing donor identification details.',
    status: 'pending',
    updatedAt: 'Updated 20 minutes ago'
  }
];
