// Shoplytics Data Formatting Utilities

export function formatBRL(value, compact = false) {
  if (value === null || value === undefined || isNaN(value)) return 'R$ 0.00';
  const num = Number(value);
  
  if (compact) {
    if (Math.abs(num) >= 1_000_000) {
      return `R$ ${(num / 1_000_000).toFixed(2)}M`;
    }
    if (Math.abs(num) >= 1_000) {
      return `R$ ${(num / 1_000).toFixed(1)}k`;
    }
  }

  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

export function formatNumber(value, compact = false) {
  if (value === null || value === undefined || isNaN(value)) return '0';
  const num = Number(value);

  if (compact) {
    if (Math.abs(num) >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(2)}M`;
    }
    if (Math.abs(num) >= 1_000) {
      return `${(num / 1_000).toFixed(1)}k`;
    }
  }

  return new Intl.NumberFormat('en-US').format(num);
}

export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined || isNaN(value)) return '0.0%';
  const num = Number(value);
  return `${num.toFixed(decimals)}%`;
}

export function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

export function exportToCSV(filename, rows) {
  if (!rows || !rows.length) {
    alert('No data available to export.');
    return;
  }

  const keys = Object.keys(rows[0]);
  const headerLine = keys.map((k) => `"${k}"`).join(',');
  const csvLines = rows.map((row) =>
    keys
      .map((key) => {
        let val = row[key];
        if (val === null || val === undefined) val = '';
        if (typeof val === 'object') val = JSON.stringify(val);
        const escaped = String(val).replace(/"/g, '""');
        return `"${escaped}"`;
      })
      .join(',')
  );

  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headerLine, ...csvLines].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `${filename}_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
