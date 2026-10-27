import React, { useState, useEffect } from 'react';
import { api, MetaData, PropertiesResponse, PropertyAnalytics } from '../api';
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Building2, 
  MapPin, 
  RotateCcw,
  BarChart2,
  Table as TableIcon
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { useTheme } from '../context/ThemeContext';

interface PropertyExplorerProps {
  meta: MetaData | null;
}

export const PropertyExplorerPage: React.FC<PropertyExplorerProps> = ({ meta }) => {
  const { isDark } = useTheme();
  const [selectedLocation, setSelectedLocation] = useState<string>('All');
  const [selectedAreaType, setSelectedAreaType] = useState<string>('All');
  const [selectedBhk, setSelectedBhk] = useState<string>('All');
  const [minPrice, setMinPrice] = useState<number>(10);
  const [maxPrice, setMaxPrice] = useState<number>(1000);
  const [search, setSearch] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(20);
  const [activeView, setActiveView] = useState<'analytics' | 'table'>('analytics');

  const [data, setData] = useState<PropertiesResponse | null>(null);
  const [analytics, setAnalytics] = useState<PropertyAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const locations = meta?.locations || [];
  const areaTypes = meta?.area_types || [];

  const handleResetFilters = () => {
    setSelectedLocation('All');
    setSelectedAreaType('All');
    setSelectedBhk('All');
    setMinPrice(10);
    setMaxPrice(1000);
    setSearch('');
    setPage(1);
  };

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    const queryParams: Record<string, any> = {
      page,
      page_size: pageSize,
      location: selectedLocation,
      area_type: selectedAreaType,
      bhk: selectedBhk !== 'All' ? Number(selectedBhk) : undefined,
      min_price: minPrice,
      max_price: maxPrice,
      search: search.trim() || undefined
    };

    Promise.all([
      api.getProperties(queryParams),
      api.getAnalytics({ location: selectedLocation, area_type: selectedAreaType })
    ])
      .then(([propRes, analyticsRes]) => {
        if (isMounted) {
          setData(propRes);
          setAnalytics(analyticsRes);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load explorer data:', err);
        if (isMounted) setLoading(false);
      });

    return () => { isMounted = false; };
  }, [page, selectedLocation, selectedAreaType, selectedBhk, minPrice, maxPrice, search]);

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#E8E4DC]">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="editorial-badge">
              <Building2 className="w-3.5 h-3.5 text-[#BC7B6F]" />
              Market Intelligence
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-serif font-bold text-[#3D221C] tracking-tight">
            Bengaluru Residential Explorer
          </h1>
          <p className="text-sm text-[#826F6A] mt-1">
            Browse and analyze 12,496 verified residential property listings across Bengaluru's top micro-markets.
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-1.5 bg-[#FFFFFF] border border-[#E8E4DC] p-1.5 rounded-full shadow-xs self-start sm:self-auto">
          <button
            onClick={() => setActiveView('analytics')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              activeView === 'analytics'
                ? 'bg-[#5A322A] text-[#FAF8F5] shadow-xs'
                : 'text-[#826F6A] hover:text-[#5A322A]'
            }`}
          >
            <BarChart2 className="w-3.5 h-3.5" /> Market Analytics
          </button>
          <button
            onClick={() => setActiveView('table')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              activeView === 'table'
                ? 'bg-[#5A322A] text-[#FAF8F5] shadow-xs'
                : 'text-[#826F6A] hover:text-[#5A322A]'
            }`}
          >
            <TableIcon className="w-3.5 h-3.5" /> Listings Index
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="editorial-card p-5">
          <span className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider block">
            Matching Properties
          </span>
          <span className="text-2xl font-serif font-bold text-[#3D221C] mt-1 block">
            {data?.total_records.toLocaleString() || '...'}
          </span>
        </div>
        <div className="editorial-card p-5">
          <span className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider block">
            Average Price
          </span>
          <span className="text-2xl font-serif font-bold text-[#BC7B6F] mt-1 block">
            {data ? `₹ ${data.summary.avg_price_lakhs}L` : '...'}
          </span>
        </div>
        <div className="editorial-card p-5">
          <span className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider block">
            Average Floor Area
          </span>
          <span className="text-2xl font-serif font-bold text-[#3D221C] mt-1 block">
            {data ? `${data.summary.avg_size_sqft.toLocaleString()} sqft` : '...'}
          </span>
        </div>
        <div className="editorial-card p-5">
          <span className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider block">
            Avg Rate / Sq.Ft.
          </span>
          <span className="text-2xl font-mono font-bold text-[#718A9E] mt-1 block">
            {data ? `₹ ${data.summary.avg_price_per_sqft.toLocaleString()}` : '...'}
          </span>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="editorial-card p-5 space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Search */}
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-4 h-4 text-[#826F6A] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by neighborhood..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full pl-9 pr-3 py-2 text-xs text-[#3D221C] placeholder-[#A89893] bg-[#FAF8F5] border border-[#D8D4CC] rounded-xl focus:bg-[#FFFFFF]"
            />
          </div>

          {/* Location Dropdown */}
          <select
            value={selectedLocation}
            onChange={(e) => { setSelectedLocation(e.target.value); setPage(1); }}
            className="px-3.5 py-2 text-xs font-medium text-[#3D221C] bg-[#FAF8F5] border border-[#D8D4CC] rounded-xl focus:bg-[#FFFFFF]"
          >
            <option value="All">All Localities</option>
            {locations.map((loc) => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>

          {/* Area Type Dropdown */}
          <select
            value={selectedAreaType}
            onChange={(e) => { setSelectedAreaType(e.target.value); setPage(1); }}
            className="px-3.5 py-2 text-xs font-medium text-[#3D221C] bg-[#FAF8F5] border border-[#D8D4CC] rounded-xl focus:bg-[#FFFFFF]"
          >
            <option value="All">All Area Types</option>
            {areaTypes.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>

          {/* BHK Dropdown */}
          <select
            value={selectedBhk}
            onChange={(e) => { setSelectedBhk(e.target.value); setPage(1); }}
            className="px-3.5 py-2 text-xs font-medium text-[#3D221C] bg-[#FAF8F5] border border-[#D8D4CC] rounded-xl focus:bg-[#FFFFFF]"
          >
            <option value="All">All Configurations</option>
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <option key={n} value={n}>{n} BHK</option>
            ))}
          </select>

          {/* Reset Filters */}
          <button
            onClick={handleResetFilters}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-[#826F6A] hover:text-[#5A322A] bg-[#FAF8F5] hover:bg-[#F2ECE6] border border-[#D8D4CC] rounded-xl transition-all cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>
      </div>

      {/* Main View Area */}
      {activeView === 'analytics' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Price Distribution */}
          <div className="editorial-card p-6">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-[#F0ECE6]">
              <h3 className="text-sm font-bold text-[#3D221C] uppercase tracking-wider flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-[#BC7B6F]" />
                Price Distribution (₹ Lakhs)
              </h3>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics?.price_distribution || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#36415A' : '#E8E4DC'} vertical={false} />
                  <XAxis dataKey="range" stroke={isDark ? '#8FA0B8' : '#826F6A'} fontSize={10} tickLine={false} />
                  <YAxis stroke={isDark ? '#8FA0B8' : '#826F6A'} fontSize={10} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: isDark ? '#202734' : '#FFFFFF', 
                      borderColor: isDark ? '#36415A' : '#CCCDC7', 
                      color: isDark ? '#F1F7EE' : '#3D221C',
                      borderRadius: '10px', 
                      boxShadow: isDark ? '0 8px 24px rgba(0,0,0,0.5)' : '0 4px 12px rgba(0,0,0,0.06)' 
                    }}
                  />
                  <Bar dataKey="count" fill={isDark ? '#B7D894' : '#BC7B6F'} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* BHK Distribution */}
          <div className="editorial-card p-6">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-[#F0ECE6]">
              <h3 className="text-sm font-bold text-[#3D221C] uppercase tracking-wider flex items-center gap-2">
                <Building2 className="w-4 h-4 text-[#718A9E]" />
                Average Valuation by BHK
              </h3>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics?.bhk_distribution || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#36415A' : '#E8E4DC'} vertical={false} />
                  <XAxis dataKey="bhk" stroke={isDark ? '#8FA0B8' : '#826F6A'} fontSize={10} tickLine={false} tickFormatter={(b) => `${b} BHK`} />
                  <YAxis stroke={isDark ? '#8FA0B8' : '#826F6A'} fontSize={10} tickLine={false} tickFormatter={(v) => `₹${v}L`} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: isDark ? '#202734' : '#FFFFFF', 
                      borderColor: isDark ? '#36415A' : '#CCCDC7', 
                      color: isDark ? '#F1F7EE' : '#3D221C',
                      borderRadius: '10px', 
                      boxShadow: isDark ? '0 8px 24px rgba(0,0,0,0.5)' : '0 4px 12px rgba(0,0,0,0.06)' 
                    }}
                    formatter={(v: any) => [`₹ ${v} Lakhs`, 'Average Price']}
                  />
                  <Bar dataKey="avg_price" fill={isDark ? '#7E97B8' : '#718A9E'} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Localities */}
          <div className="editorial-card p-6 md:col-span-2">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-[#F0ECE6]">
              <h3 className="text-sm font-bold text-[#3D221C] uppercase tracking-wider flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#BC7B6F]" />
                Prominent Micro-Market Valuations (Average Price in Lakhs)
              </h3>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics?.top_localities || []} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#36415A' : '#E8E4DC'} horizontal={false} />
                  <XAxis type="number" stroke={isDark ? '#8FA0B8' : '#826F6A'} fontSize={10} tickFormatter={(v) => `₹${v}L`} />
                  <YAxis dataKey="location" type="category" stroke={isDark ? '#8FA0B8' : '#826F6A'} fontSize={10} width={140} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: isDark ? '#202734' : '#FFFFFF', 
                      borderColor: isDark ? '#36415A' : '#CCCDC7', 
                      color: isDark ? '#F1F7EE' : '#3D221C',
                      borderRadius: '10px', 
                      boxShadow: isDark ? '0 8px 24px rgba(0,0,0,0.5)' : '0 4px 12px rgba(0,0,0,0.06)' 
                    }}
                    formatter={(v: any) => [`₹ ${v} Lakhs`, 'Average Price']}
                  />
                  <Bar dataKey="avg_price" fill={isDark ? '#B7D894' : '#5A322A'} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        /* Table View */
        <div className="editorial-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAF8F5] border-b border-[#E8E4DC] text-[#5A322A] font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Locality</th>
                  <th className="py-3.5 px-4">Area Type</th>
                  <th className="py-3.5 px-4">BHK</th>
                  <th className="py-3.5 px-4">Baths</th>
                  <th className="py-3.5 px-4">Floor Area</th>
                  <th className="py-3.5 px-4">Price (Lakhs)</th>
                  <th className="py-3.5 px-4">Rate / Sq.Ft.</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F0ECE6] text-[#5A322A]">
                {data?.records.map((r) => (
                  <tr key={r.id} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#3D221C]">{r.location}</td>
                    <td className="py-3 px-4 text-[#826F6A]">{r.area_type}</td>
                    <td className="py-3 px-4">{r.bhk} BHK</td>
                    <td className="py-3 px-4">{r.bath} Bath</td>
                    <td className="py-3 px-4 font-mono">{r.size_sqft.toLocaleString()} sqft</td>
                    <td className="py-3 px-4 font-serif font-bold text-[#BC7B6F]">₹ {r.price_lakhs}L</td>
                    <td className="py-3 px-4 text-[#718A9E] font-mono">₹ {r.price_per_sqft.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between p-4 bg-[#FAF8F5] border-t border-[#E8E4DC] text-xs text-[#826F6A]">
            <span>
              Page {data?.page} of {data?.total_pages || 1}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-1.5 rounded-lg bg-[#FFFFFF] border border-[#D8D4CC] text-[#5A322A] hover:bg-[#F3EFEA] disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(data?.total_pages || 1, p + 1))}
                disabled={page >= (data?.total_pages || 1)}
                className="p-1.5 rounded-lg bg-[#FFFFFF] border border-[#D8D4CC] text-[#5A322A] hover:bg-[#F3EFEA] disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
