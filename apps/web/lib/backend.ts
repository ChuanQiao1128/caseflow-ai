import { demoMatter } from '../data/demo-data';

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

function trimTrailingSlash(value: string) {
  return value.replace(/\/$/, '');
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

export async function loadBackendHealth(): Promise<BackendHealth> {
  const baseUrl = getApiBaseUrl();
  if (!baseUrl) {
    return {
      status: 'demo',
      label: 'Demo mode',
      detail: 'Set CASEFLOW_API_BASE_URL to connect this frontend to the FastAPI backend.'
    };
  }

  try {
    const health = await fetchJson<{ status: string }>('/health');
    if (health.status === 'ok') {
      return {
        status: 'ok',
        label: 'Backend connected',
        detail: `FastAPI is reachable at ${baseUrl}`
      };
    }
    return {
      status: 'offline',
      label: 'Backend response unexpected',
      detail: `Received ${health.status} from ${baseUrl}/health`
    };
  } catch {
    return {
      status: 'offline',
      label: 'Backend offline',
      detail: `Could not reach ${baseUrl}`
    };
  }
}

export async function loadMatterList(): Promise<BackendMatter[]> {
  const baseUrl = getApiBaseUrl();
  const organisationId = getDemoOrganisationId();
  if (!baseUrl || !organisationId) {
    return [
      {
        id: demoMatter.id,
        organisation_id: 'demo-org',
        reference: 'DEMO-001',
        title: demoMatter.title,
        status: demoMatter.status,
        created_at: new Date().toISOString(),
        updated_at: null
      }
    ];
  }

  try {
    return await fetchJson<BackendMatter[]>(`/organisations/${organisationId}/matters`);
  } catch {
    return [];
  }
}

export async function loadMatterById(matterId: string): Promise<BackendMatter | null> {
  const baseUrl = getApiBaseUrl();
  const organisationId = getDemoOrganisationId();
  if (!baseUrl || !organisationId) {
    if (matterId === demoMatter.id) {
      return {
        id: demoMatter.id,
        organisation_id: 'demo-org',
        reference: 'DEMO-001',
        title: demoMatter.title,
        status: demoMatter.status,
        created_at: new Date().toISOString(),
        updated_at: null
      };
    }
    return null;
  }

  try {
    const matters = await loadMatterList();
    return matters.find((matter) => matter.id === matterId) ?? null;
  } catch {
    return null;
  }
}
