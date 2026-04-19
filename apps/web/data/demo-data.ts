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
  riskLevel?: 'high' | 'medium' | 'low';
  openQueueItems?: number;
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
  settlementDate: '2026-05-14',
  client: 'Ngata Family',
  lastUpdated: 'Updated 8 minutes ago',
  reference: 'DEMO-001',
  riskLevel: 'high',
  openQueueItems: 2
};

export const demoMatterList: MatterDemo[] = [
  demoMatter,
  {
    id: 'matter-002',
    title: 'Hamilton Vendor Discharge · Patel',
    organisation: 'Kauri Coast Legal',
    type: 'Individual vendor + discharge',
    status: 'Draft',
    settlementDate: '2026-05-26',
    client: 'Patel',
    lastUpdated: 'Updated 30 minutes ago',
    reference: 'DEMO-002',
    riskLevel: 'medium',
    openQueueItems: 1
  },
  {
    id: 'matter-003',
    title: 'Trust Buyer Mortgage + CDD · Rimu Trust',
    organisation: 'Harbour Chambers',
    type: 'Trust buyer + mortgage + CDD',
    status: 'Needs human review',
    settlementDate: '2026-05-10',
    client: 'Rimu Trust',
    lastUpdated: 'Updated 4 minutes ago',
    reference: 'DEMO-003',
    riskLevel: 'high',
    openQueueItems: 3
  },
  {
    id: 'matter-004',
    title: 'Trust Vendor Deed Variation · Tui Trustees',
    organisation: 'Southern Legal',
    type: 'Trust vendor + deed variation + discharge',
    status: 'Ready for review',
    settlementDate: '2026-06-03',
    client: 'Tui Trustees',
    lastUpdated: 'Updated 2 hours ago',
    reference: 'DEMO-004',
    riskLevel: 'low',
    openQueueItems: 0
  }
];

export const demoWorkflowSteps: WorkflowStep[] = [
  {
    name: '接收并分类文件',
    summary: '已导入合成交割材料并完成基础分类。',
    state: 'done'
  },
  {
    name: '抽取关键字段',
    summary: '已抽取贷款方、交割日、交易主体等信息。',
    state: 'done'
  },
  {
    name: '执行规则审查',
    summary: '地址证明与保险起保时间存在待核对项。',
    state: 'active'
  },
  {
    name: '进入人工审批',
    summary: '外联邮件草稿已进入待审批队列。',
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
  { label: '文件总数', value: '3', hint: '该案件已登记的合成材料' },
  { label: '已抽取字段', value: '3', hint: '均附带来源页码可回溯' },
  { label: '队列待办', value: '2', hint: '等待人工审批的可执行动作' },
  { label: '证据可信度', value: '高', hint: '证据不足时会明确标记待核对' }
];
