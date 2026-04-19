'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import type { BackendMatter } from '../lib/backend';

type RiskFilter = 'all' | 'high' | 'medium' | 'low';
type SortMode = 'risk' | 'settlement' | 'queue';

function statusLabel(status: string) {
  const normalized = status.toLowerCase();
  if (normalized.includes('needs human review') || normalized.includes('needs_human_review')) return '需人工复核';
  if (normalized.includes('unclear')) return '待核对';
  if (normalized.includes('approved') || normalized.includes('ready')) return '可复核';
  if (normalized.includes('draft')) return '草稿';
  return status;
}

function riskLabel(risk?: BackendMatter['risk_level']) {
  if (risk === 'high') return '高风险';
  if (risk === 'medium') return '中风险';
  if (risk === 'low') return '低风险';
  return '风险未知';
}

function formatSettlementDate(value?: string | null) {
  if (!value) return '交割日未知';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat('en-NZ', { dateStyle: 'medium' }).format(parsed);
}

function riskRank(risk?: BackendMatter['risk_level']) {
  if (risk === 'high') return 3;
  if (risk === 'medium') return 2;
  if (risk === 'low') return 1;
  return 0;
}

function settlementTimestamp(value?: string | null) {
  if (!value) return Number.POSITIVE_INFINITY;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? Number.POSITIVE_INFINITY : parsed.getTime();
}

export function MatterList({ matters }: { matters: BackendMatter[] }) {
  const [riskFilter, setRiskFilter] = useState<RiskFilter>('all');
  const [sortMode, setSortMode] = useState<SortMode>('risk');

  const visibleMatters = useMemo(() => {
    const filtered = matters.filter((matter) => (riskFilter === 'all' ? true : matter.risk_level === riskFilter));

    const sorted = [...filtered].sort((a, b) => {
      if (sortMode === 'risk') {
        return riskRank(b.risk_level) - riskRank(a.risk_level);
      }
      if (sortMode === 'settlement') {
        return settlementTimestamp(a.settlement_date) - settlementTimestamp(b.settlement_date);
      }
      return (b.open_queue_items ?? 0) - (a.open_queue_items ?? 0);
    });

    return sorted;
  }, [matters, riskFilter, sortMode]);

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">案件清单</p>
          <h2>可进入的案件</h2>
        </div>
        <span className="pill">{visibleMatters.length} / {matters.length} 个案件</span>
      </div>

      <div className="list-controls">
        <label className="control-item">
          <span className="label">风险筛选</span>
          <select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value as RiskFilter)}>
            <option value="all">全部</option>
            <option value="high">高风险</option>
            <option value="medium">中风险</option>
            <option value="low">低风险</option>
          </select>
        </label>

        <label className="control-item">
          <span className="label">排序方式</span>
          <select value={sortMode} onChange={(event) => setSortMode(event.target.value as SortMode)}>
            <option value="risk">按风险优先</option>
            <option value="settlement">按交割日期</option>
            <option value="queue">按待办数量</option>
          </select>
        </label>
      </div>

      <div className="matter-list">
        {visibleMatters.map((matter) => (
          <Link key={matter.id} href={`/matters/${matter.id}`} className="matter-list-item">
            <div>
              <span className="label">{matter.reference ?? '无参考号'}</span>
              <strong>{matter.title}</strong>
              <p>{statusLabel(matter.status)}</p>
              <div className="matter-tags">
                <span className="pill">{riskLabel(matter.risk_level)}</span>
                <span className="pill">{formatSettlementDate(matter.settlement_date)}</span>
                <span className="pill">待办 {(matter.open_queue_items ?? 0).toString()}</span>
              </div>
            </div>
            <span className="matter-chevron">→</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
