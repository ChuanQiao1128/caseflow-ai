import { demoAuditLogs, demoChecklist, demoDocuments, demoEvidence, demoFields, demoMatter, demoQueueItems, demoReview } from '../data/demo-data';

export type BackendHealth = {
  status: 'ok' | 'demo' | 'offline';
  label: string;
  detail: string;
};

export type BackendMatter = {
  id: string;
  organisation_id: string;
  reference: string | null;
  title: string;
  status: string;
  created_at: string;
  updated_at: string | null;
};

export type BackendDocument = {
  id: string;
  matter_id: string;
  filename: string;
  mime_type: string;
  storage_key: string;
  created_at: string;
  updated_at: string | null;
};

export type BackendAuditLog = {
  id: string;
  organisation_id: string;
  actor_user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  details: Record<string, unknown>;
  created_at: string;
  updated_at: string | null;
};

export type BackendApprovalQueueItem = {
  id: string;
  organisation_id: string;
  matter_id: string;
  item_type: 'follow_up_email_draft';
  status: 'pending' | 'approved' | 'rejected' | 'needs_changes';
  subject: string;
  body: string;
  reviewer_notes: string | null;
};

export type WorkspaceMatter = {
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

export type WorkspaceDocument = {
  id: string;
  name: string;
  pages: string;
  tag: string;
};

export type WorkspaceQueueItem = {
  id: string;
  matterId: string;
  subject: string;
  context: string;
  reason: string;
  status: 'pending' | 'needs_changes' | 'approved';
  updatedAt: string;
  reviewerNotes?: string | null;
};

export type WorkspaceAuditLog = {
  id: string;
  action: string;
  entityType: string;
  entityId: string;
  details: string;
  createdAt: string;
};

export type WorkspaceAnalysis = {
  evidence: typeof demoEvidence;
  fields: typeof demoFields;
  checklist: typeof demoChecklist;
  review: typeof demoReview;
};

export type MatterWorkspaceState = {
  backend: BackendHealth;
  mode: 'demo' | 'live';
  matter: WorkspaceMatter;
  documents: WorkspaceDocument[];
  queueItems: WorkspaceQueueItem[];
  auditLogs: WorkspaceAuditLog[];
  analysis: WorkspaceAnalysis;
};

export type QueuePageState = {
  backend: BackendHealth;
  mode: 'demo' | 'live';
  matter: WorkspaceMatter;
  queueItems: WorkspaceQueueItem[];
};

function trimTrailingSlash(value: string) {
  return value.replace(/\/$/, '');
}

function formatTimestamp(value: string | null | undefined) {
  if (!value) {
    return 'Unknown time';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat('en-NZ', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date);
}

export function getApiBaseUrl() {
  const raw = process.env.CASEFLOW_API_BASE_URL || process.env.NEXT_PUBLIC_CASEFLOW_API_BASE_URL;
  return raw ? trimTrailingSlash(raw) : null;
}

export function getDemoOrganisationId() {
  return process.env.CASEFLOW_DEMO_ORGANISATION_ID || null;
}

async function fetchJson<T>(path: string): Promise<T> {
  const baseUrl = getApiBaseUrl();
  if (!baseUrl) {
    throw new Error('No API base URL configured');
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2200);
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      cache: 'no-store',
      signal: controller.signal
    });
    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }
    return (await response.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

async function fetchOptionalJson<T>(path: string): Promise<T | null> {
  try {
    return await fetchJson<T>(path);
  } catch {
    return null;
  }
}

function getLiveContext() {
  const baseUrl = getApiBaseUrl();
  const organisationId = getDemoOrganisationId();
  if (!baseUrl || !organisationId) {
    return null;
  }
  return { baseUrl, organisationId };
}

export async function loadBackendHealth(): Promise<BackendHealth> {
  const context = getLiveContext();
  if (!context) {
    return {
      status: 'demo',
      label: 'Demo mode',
      detail: 'Set CASEFLOW_API_BASE_URL and CASEFLOW_DEMO_ORGANISATION_ID to connect this frontend to the FastAPI backend.'
    };
  }

  try {
    const health = await fetchJson<{ status: string }>('/health');
    if (health.status === 'ok') {
      return {
        status: 'ok',
        label: 'Backend connected',
        detail: `FastAPI is reachable at ${context.baseUrl}`
      };
    }
    return {
      status: 'offline',
      label: 'Backend response unexpected',
      detail: `Received ${health.status} from ${context.baseUrl}/health`
    };
  } catch {
    return {
      status: 'offline',
      label: 'Backend offline',
      detail: `Could not reach ${context.baseUrl}`
    };
  }
}

export async function loadMatterList(): Promise<BackendMatter[]> {
  const context = getLiveContext();
  if (!context) {
    return [
      {
        id: demoMatter.id,
        organisation_id: 'demo-org',
        reference: demoMatter.reference ?? 'DEMO-001',
        title: demoMatter.title,
        status: demoMatter.status,
        created_at: new Date().toISOString(),
        updated_at: null
      }
    ];
  }

  const response = await fetchOptionalJson<BackendMatter[]>(`/organisations/${context.organisationId}/matters`);
  return response && response.length > 0 ? response : [];
}

export async function loadMatterById(matterId: string): Promise<BackendMatter | null> {
  const context = getLiveContext();
  if (!context) {
    if (matterId === demoMatter.id) {
      return {
        id: demoMatter.id,
        organisation_id: 'demo-org',
        reference: demoMatter.reference ?? 'DEMO-001',
        title: demoMatter.title,
        status: demoMatter.status,
        created_at: new Date().toISOString(),
        updated_at: null
      };
    }
    return null;
  }

  return fetchOptionalJson<BackendMatter>(`/organisations/${context.organisationId}/matters/${matterId}`);
}

export async function loadDocumentsForMatter(matterId: string): Promise<WorkspaceDocument[]> {
  const context = getLiveContext();
  if (!context) {
    return demoDocuments;
  }

  const documents = await fetchOptionalJson<BackendDocument[]>(
    `/organisations/${context.organisationId}/matters/${matterId}/documents`
  );
  if (!documents || documents.length === 0) {
    return [];
  }

  return documents.map((document) => ({
    id: document.id,
    name: document.filename,
    pages: `Registered ${formatTimestamp(document.created_at)}`,
    tag: document.mime_type
  }));
}

export async function loadAuditLogsForMatter(matterId: string): Promise<WorkspaceAuditLog[]> {
  const context = getLiveContext();
  if (!context) {
    return demoAuditLogs;
  }

  const logs = await fetchOptionalJson<BackendAuditLog[]>(
    `/organisations/${context.organisationId}/matters/${matterId}/audit-logs`
  );
  if (!logs || logs.length === 0) {
    return [];
  }

  return logs.map((log) => ({
    id: log.id,
    action: log.action,
    entityType: log.entity_type,
    entityId: log.entity_id,
    details: Object.entries(log.details)
      .map(([key, value]) => `${key}: ${String(value)}`)
      .join(' · '),
    createdAt: formatTimestamp(log.created_at)
  }));
}

export async function loadApprovalQueueForMatter(matterId: string): Promise<WorkspaceQueueItem[]> {
  const context = getLiveContext();
  if (!context) {
    return demoQueueItems;
  }

  const items = await fetchOptionalJson<BackendApprovalQueueItem[]>(
    `/organisations/${context.organisationId}/matters/${matterId}/approval-queue`
  );
  if (!items || items.length === 0) {
    return [];
  }

  return items.map((item) => ({
    id: item.id,
    matterId: item.matter_id,
    subject: item.subject,
    context: item.body,
    reason: item.reviewer_notes ?? item.body,
    status: item.status === 'rejected' ? 'needs_changes' : item.status,
    updatedAt: 'Updated ' + new Intl.DateTimeFormat('en-NZ', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date()),
    reviewerNotes: item.reviewer_notes
  }));
}

function buildDemoWorkspace(): MatterWorkspaceState {
  return {
    backend: {
      status: 'demo',
      label: 'Demo mode',
      detail: 'Synthetic data is active. Configure backend environment variables to connect live.'
    },
    mode: 'demo',
    matter: { ...demoMatter, reference: demoMatter.reference ?? null },
    documents: demoDocuments,
    queueItems: demoQueueItems,
    auditLogs: demoAuditLogs,
    analysis: {
      evidence: demoEvidence,
      fields: demoFields,
      checklist: demoChecklist,
      review: demoReview
    }
  };
}

export async function loadMatterWorkspace(matterId: string): Promise<MatterWorkspaceState | null> {
  const backend = await loadBackendHealth();
  if (backend.status !== 'ok') {
    if (matterId !== demoMatter.id && getLiveContext() === null) {
      return buildDemoWorkspace();
    }
    return buildDemoWorkspace();
  }

  const matter = await loadMatterById(matterId);
  if (!matter) {
    return null;
  }

  const [documents, queueItems, auditLogs] = await Promise.all([
    loadDocumentsForMatter(matterId),
    loadApprovalQueueForMatter(matterId),
    loadAuditLogsForMatter(matterId)
  ]);

  return {
    backend,
    mode: 'live',
    matter: {
      id: matter.id,
      title: matter.title,
      organisation: `Organisation ${matter.organisation_id.slice(0, 8)}`,
      type: 'Live backend matter',
      status: matter.status,
      settlementDate: 'Not yet extracted',
      client: matter.reference ?? 'Live backend matter',
      lastUpdated: `Updated ${formatTimestamp(matter.updated_at ?? matter.created_at)}`,
      reference: matter.reference
    },
    documents,
    queueItems,
    auditLogs,
    analysis: {
      evidence: demoEvidence,
      fields: demoFields,
      checklist: demoChecklist,
      review: {
        ...demoReview,
        summary: 'Synthetic analysis preview. Live read endpoints for extraction and checklist data are not yet wired.'
      }
    }
  };
}

export async function loadQueuePageState(): Promise<QueuePageState> {
  const backend = await loadBackendHealth();
  if (backend.status !== 'ok') {
    return {
      backend,
      mode: 'demo',
      matter: { ...demoMatter, reference: demoMatter.reference ?? null },
      queueItems: demoQueueItems
    };
  }

  const matters = await loadMatterList();
  if (matters.length === 0) {
    return {
      backend,
      mode: 'demo',
      matter: { ...demoMatter, reference: demoMatter.reference ?? null },
      queueItems: demoQueueItems
    };
  }

  const selectedMatter = matters[0];
  const queueItems = await loadApprovalQueueForMatter(selectedMatter.id);

  return {
    backend,
    mode: 'live',
    matter: {
      id: selectedMatter.id,
      title: selectedMatter.title,
      organisation: `Organisation ${selectedMatter.organisation_id.slice(0, 8)}`,
      type: 'Live backend matter',
      status: selectedMatter.status,
      settlementDate: 'Not yet extracted',
      client: selectedMatter.reference ?? 'Live backend matter',
      lastUpdated: `Updated ${formatTimestamp(selectedMatter.updated_at ?? selectedMatter.created_at)}`,
      reference: selectedMatter.reference
    },
    queueItems
  };
}
