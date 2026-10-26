import React, { useState } from 'react';
import { 
  Building2, 
  BarChart3, 
  Search, 
  FlaskConical, 
  Cpu, 
  Sparkles, 
  BookOpen, 
  Menu,
  X
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  apiHealthy: boolean | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, apiHealthy }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'prediction', label: 'Valuation Studio', icon: Sparkles },
    { id: 'explorer', label: 'Property Explorer', icon: Search },
    { id: 'lab', label: 'Model Lab', icon: FlaskConical },
    { id: 'explainability', label: 'Explainability', icon: Cpu },
    { id: 'methodology', label: 'Methodology', icon: BookOpen },
  ];

  const handleNavClick = (id: string) => {
    setActiveTab(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[#E8E4DC] bg-[#FAF8F5]/90 backdrop-blur-md transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Distinctive Editorial Wordmark */}
          <div 
            className="flex items-center gap-3 cursor-pointer group shrink-0" 
            onClick={() => handleNavClick('overview')}
          >
            <div className="w-10 h-10 rounded-lg bg-[#5A322A] flex items-center justify-center text-[#FAF8F5] shadow-sm group-hover:bg-[#BC7B6F] transition-colors shrink-0">
              <Building2 className="w-5 h-5 text-[#E4A499]" />
            </div>
            <div className="shrink-0">
              <div className="flex items-center gap-2">
                <span className="font-serif font-bold text-xl xl:text-2xl text-[#3D221C] tracking-tight whitespace-nowrap">
                  SMART ESTATE <span className="text-[#BC7B6F] font-normal italic">AI</span>
                </span>
                <span className="text-[10px] font-sans font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#F3EBE8] text-[#BC7B6F] border border-[#E8D4D0] whitespace-nowrap">
                  PropTech
                </span>
              </div>
              <p className="text-[11px] font-sans text-[#826F6A] tracking-wider uppercase hidden xl:block whitespace-nowrap">
                Bengaluru Real Estate Valuation & Research
              </p>
            </div>
          </div>

          {/* Desktop Editorial Navigation */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-1.5 bg-[#FFFFFF] p-1.5 rounded-full border border-[#E8E4DC] shadow-sm shrink-0">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`inline-flex items-center justify-center gap-1.5 xl:gap-2 px-2.5 xl:px-3.5 py-1.5 rounded-full text-[11px] xl:text-xs font-semibold tracking-normal whitespace-nowrap transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[#5A322A] text-[#FAF8F5] shadow-xs'
                      : 'text-[#5A322A]/80 hover:text-[#3D221C] hover:bg-[#F4EFEB]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-[#E4A499]' : 'text-[#826F6A]'}`} />
                  <span className="whitespace-nowrap">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Status Badge & Mobile Trigger */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="hidden sm:flex items-center gap-2 text-xs px-3 py-1.5 rounded-full bg-[#FFFFFF] border border-[#E8E4DC] shadow-xs text-[#5A322A] whitespace-nowrap">
              {apiHealthy === true ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-[#718A9E] animate-pulse shrink-0"></span>
                  <span className="font-mono text-[11px] font-semibold text-[#5A322A]">FastAPI Active</span>
                </>
              ) : apiHealthy === false ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-[#BC7B6F] shrink-0"></span>
                  <span className="font-mono text-[11px] font-semibold text-[#BC7B6F]">API Offline</span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 rounded-full bg-[#CCCDC7] animate-ping shrink-0"></span>
                  <span className="font-mono text-[11px] text-[#826F6A]">Connecting...</span>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg bg-[#FFFFFF] border border-[#E8E4DC] text-[#5A322A] hover:bg-[#F4EFEB]"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-[#E8E4DC] bg-[#FAF8F5] px-4 pt-3 pb-5 space-y-1 shadow-lg animate-fadeIn">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-[#5A322A] text-[#FAF8F5]'
                    : 'text-[#5A322A] hover:bg-[#F3ECE8]'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#E4A499]' : 'text-[#BC7B6F]'}`} />
                {item.label}
              </button>
            );
          })}
          <div className="pt-2 border-t border-[#E8E4DC] mt-2 flex items-center justify-between text-xs text-[#826F6A] px-2">
            <span>FastAPI Backend (:8000)</span>
            <span className={apiHealthy ? 'text-[#718A9E] font-medium' : 'text-[#BC7B6F]'}>
              {apiHealthy ? '● Online' : '○ Checking...'}
            </span>
          </div>
        </div>
      )}
    </header>
  );
};
