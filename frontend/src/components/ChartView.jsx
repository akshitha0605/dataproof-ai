import React from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { BarChart3, TrendingUp, PieChart as PieIcon, Activity } from 'lucide-react';

const COLORS = ['#06b6d4', '#10b981', '#6366f1', '#f59e0b', '#ec4899', '#8b5cf6', '#3b82f6'];

export default function ChartView({ chartData }) {
  if (!chartData || !chartData.data || chartData.data.length === 0 || chartData.chart_type === 'none') {
    return null;
  }

  const { chart_type, title, x_axis, y_axis, data } = chartData;

  const renderKPI = () => {
    const mainVal = data[0] ? (data[0][y_axis] ?? data[0].value ?? data[0].Total ?? 'N/A') : 'N/A';
    return (
      <div className="flex flex-col items-center justify-center py-8 space-y-2 text-center">
        <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">{title}</div>
        <div className="text-4xl font-black text-slate-100 font-mono">
          {typeof mainVal === 'number' ? mainVal.toLocaleString() : mainVal}
        </div>
        <div className="text-xs text-slate-500 font-mono">Verified Execution Metric</div>
      </div>
    );
  };

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey={x_axis} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} angle={-25} textAnchor="end" />
        <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
        <Tooltip
          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
        />
        <Bar dataKey={y_axis} fill="#06b6d4" radius={[6, 6, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );

  const renderLineChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey={x_axis} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
        <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
        <Tooltip
          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
        />
        <Line type="monotone" dataKey={y_axis} stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: '#10b981' }} />
      </LineChart>
    </ResponsiveContainer>
  );

  const renderPieChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          dataKey={y_axis}
          nameKey={x_axis}
          cx="50%"
          cy="50%"
          outerRadius={100}
          innerRadius={50}
          paddingAngle={3}
          label
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
        />
        <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
      </PieChart>
    </ResponsiveContainer>
  );

  return (
    <div className="rounded-2xl glass-panel border border-slate-800 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {chart_type === 'bar' && <BarChart3 className="w-4 h-4 text-cyan-400" />}
          {chart_type === 'line' && <TrendingUp className="w-4 h-4 text-emerald-400" />}
          {chart_type === 'pie' && <PieIcon className="w-4 h-4 text-indigo-400" />}
          {chart_type === 'kpi' && <Activity className="w-4 h-4 text-amber-400" />}
          <h4 className="text-sm font-bold text-slate-100">{title}</h4>
        </div>
        <span className="text-[11px] font-mono text-slate-500 uppercase">{chart_type} Chart</span>
      </div>

      <div className="pt-2">
        {chart_type === 'kpi' && renderKPI()}
        {chart_type === 'bar' && renderBarChart()}
        {chart_type === 'line' && renderLineChart()}
        {chart_type === 'pie' && renderPieChart()}
        {chart_type !== 'kpi' && chart_type !== 'bar' && chart_type !== 'line' && chart_type !== 'pie' && renderBarChart()}
      </div>
    </div>
  );
}
