const API_BASE = '/api';

export async function uploadDatasetFile(file, sheetName = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (sheetName) {
    formData.append('sheet_name', sheetName);
  }

  const response = await fetch(`${API_BASE}/datasets/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload dataset.');
  }

  return response.json();
}

export async function fetchDatasets() {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error('Failed to fetch dataset list.');
  return res.json();
}

export async function fetchDatasetProfile(datasetId, sheetName = null) {
  const url = new URL(`${window.location.origin}${API_BASE}/datasets/${datasetId}/profile`);
  if (sheetName) url.searchParams.append('sheet_name', sheetName);

  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch dataset profile.');
  return res.json();
}

export async function fetchDatasetPreview(datasetId, page = 1, pageSize = 20, search = '', sheetName = null) {
  const url = new URL(`${window.location.origin}${API_BASE}/datasets/${datasetId}/preview`);
  url.searchParams.append('page', page);
  url.searchParams.append('page_size', pageSize);
  if (search) url.searchParams.append('search', search);
  if (sheetName) url.searchParams.append('sheet_name', sheetName);

  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch dataset preview.');
  return res.json();
}

export async function analyzeQuestion({
  datasetIds,
  sheetName = null,
  question,
  selectedAmbiguousColumn = null,
  followUpContext = null,
}) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataset_ids: datasetIds,
      sheet_name: sheetName,
      question,
      selected_ambiguous_column: selectedAmbiguousColumn,
      follow_up_context: followUpContext,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Analysis request failed.');
  }

  return res.json();
}

export async function fetchAnalysisHistory() {
  const res = await fetch(`${API_BASE}/analysis-history`);
  if (!res.ok) throw new Error('Failed to fetch analysis history.');
  return res.json();
}
