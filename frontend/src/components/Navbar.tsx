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
  X, 
  Sun, 
  Moon 
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  apiHealthy: boolean | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, apiHealthy }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isDark, toggleTheme } = useTheme();

  const navItems = [
    { id: 'overview', label: 'Overview', shortLabel: 'Overview', icon: BarChart3 },
    { id: 'prediction', label: 'Valuation Studio', shortLabel: 'Valuation', icon: Sparkles },
    { id: 'explorer', label: 'Property Explorer', shortLabel: 'Explorer', icon: Search },
    { id: 'lab', label: 'Model Lab', shortLabel: 'Model Lab', icon: FlaskConical },
    { id: 'explainability', label: 'Explainability', shortLabel: 'Explainability', icon: Cpu },
    { id: 'methodology', label: 'Methodology', shortLabel: 'Methodology', icon: BookOpen },
  ];

  const handleNavClick = (id: string) => {
    setActiveTab(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className={`sticky top-0 z-50 w-full border-b backdrop-blur-md transition-colors duration-200 ${
      isDark
        ? 'border-[#36415A] bg-[#202734]/95 text-[#D2DCE6]'
        : 'border-[#E8E4DC] bg-[#FAF8F5]/92 text-[#5A322A]'
    }`}>
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-18 sm:h-20 gap-2 sm:gap-4">
          
          {/* Distinctive Editorial Wordmark */}
          <div 
            className="flex items-center gap-2.5 cursor-pointer group shrink-0" 
            onClick={() => handleNavClick('overview')}
          >
            <div className={`w-9 h-9 rounded-lg flex items-center justify-center shadow-sm transition-colors shrink-0 ${
              isDark 
                ? 'bg-[#36415A] text-[#E0F8C7] group-hover:bg-[#455372]' 
                : 'bg-[#5A322A] text-[#FAF8F5] group-hover:bg-[#BC7B6F]'
            }`}>
              <Building2 className={`w-4 h-4 ${isDark ? 'text-[#B7D894]' : 'text-[#E4A499]'}`} />
            </div>
            <div className="shrink-0">
              <div className="flex items-center gap-1.5 sm:gap-2">
                <span className={`font-serif font-bold text-lg lg:text-xl tracking-tight whitespace-nowrap ${
                  isDark ? 'text-[#F1F7EE]' : 'text-[#3D221C]'
                }`}>
                  SMART ESTATE <span className={`${isDark ? 'text-[#B7D894]' : 'text-[#BC7B6F]'} font-normal italic`}>AI</span>
                </span>
                <span className={`text-[9px] font-sans font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-full border whitespace-nowrap ${
                  isDark
                    ? 'bg-[#36415A] text-[#B7D894] border-[#4B5E7F]'
                    : 'bg-[#F3EBE8] text-[#BC7B6F] border-[#E8D4D0]'
                }`}>
                  PropTech
                </span>
              </div>
              <p className={`text-[10px] font-sans tracking-wider uppercase hidden 2xl:block whitespace-nowrap ${
                isDark ? 'text-[#8FA0B8]' : 'text-[#826F6A]'
              }`}>
                Bengaluru Real Estate Valuation & Research
              </p>
            </div>
          </div>

          {/* Desktop Editorial Navigation (Responsively sized so it never crowds out the right badge) */}
          <nav className={`hidden lg:flex items-center gap-1 p-1 rounded-full border shadow-sm shrink-0 transition-colors ${
            isDark
              ? 'bg-[#273042] border-[#36415A]'
              : 'bg-[#FFFFFF] border-[#E8E4DC]'
          }`}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`inline-flex items-center justify-center gap-1.5 px-2.5 xl:px-3 py-1.5 rounded-full text-[11px] xl:text-xs font-semibold tracking-normal whitespace-nowrap transition-all cursor-pointer ${
                    isActive
                      ? isDark
                        ? 'bg-[#36415A] text-[#E0F8C7] shadow-xs'
                        : 'bg-[#5A322A] text-[#FAF8F5] shadow-xs'
                      : isDark
                        ? 'text-[#CBD5E1] hover:text-[#FFFFFF] hover:bg-[#303B4E]'
                        : 'text-[#5A322A]/80 hover:text-[#3D221C] hover:bg-[#F4EFEB]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 shrink-0 ${
                    isActive 
                      ? isDark ? 'text-[#B7D894]' : 'text-[#E4A499]'
                      : isDark ? 'text-[#8FA0B8]' : 'text-[#826F6A]'
                  }`} />
                  <span className="hidden xl:inline whitespace-nowrap">{item.label}</span>
                  <span className="inline xl:hidden whitespace-nowrap">{item.shortLabel}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Status Badge & Theme Switcher (Properly fitted, never overflowing) */}
          <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
            {/* Sleek Theme Toggle Icon Button */}
            <button
              type="button"
              onClick={toggleTheme}
              aria-label="Toggle Theme"
              className={`w-8 h-8 sm:w-8.5 sm:h-8.5 rounded-full border shadow-xs flex items-center justify-center transition-all cursor-pointer shrink-0 ${
                isDark
                  ? 'bg-[#273042] border-[#36415A] text-[#B7D894] hover:border-[#B7D894] hover:bg-[#303B4E]'
                  : 'bg-[#FFFFFF] border-[#E8E4DC] text-[#BC7B6F] hover:bg-[#F4EFEB]'
              }`}
              title={isDark ? "Switch to Light Theme" : "Switch to Dark Theme"}
            >
              {isDark ? (
                <Moon className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#B7D894]" />
              ) : (
                <Sun className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#BC7B6F]" />
              )}
            </button>

            {/* FastAPI Active Badge (Fitted properly without overflow) */}
            <div className={`flex items-center gap-1.5 sm:gap-2 text-xs px-2.5 sm:px-3 py-1.5 rounded-full border shadow-xs whitespace-nowrap transition-colors shrink-0 ${
              isDark
                ? 'bg-[#273042] border-[#36415A] text-[#D2DCE6]'
                : 'bg-[#FFFFFF] border-[#E8E4DC] text-[#5A322A]'
            }`}>
              {apiHealthy === true ? (
                <>
                  <span className={`w-2 h-2 rounded-full animate-pulse shrink-0 ${
                    isDark ? 'bg-[#B7D894]' : 'bg-[#718A9E]'
                  }`}></span>
                  <span className={`font-mono text-[11px] font-semibold tracking-tight ${
                    isDark ? 'text-[#E0F8C7]' : 'text-[#5A322A]'
                  }`}>
                    FastAPI Active
                  </span>
                </>
              ) : apiHealthy === false ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-[#BC7B6F] shrink-0"></span>
                  <span className="font-mono text-[11px] font-semibold text-[#BC7B6F]">API Offline</span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 rounded-full bg-[#CCCDC7] animate-ping shrink-0"></span>
                  <span className={`font-mono text-[11px] ${
                    isDark ? 'text-[#8FA0B8]' : 'text-[#826F6A]'
                  }`}>Connecting...</span>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className={`lg:hidden p-2 rounded-lg border transition-colors shrink-0 ${
                isDark
                  ? 'bg-[#273042] border-[#36415A] text-[#D2DCE6] hover:bg-[#303B4E]'
                  : 'bg-[#FFFFFF] border-[#E8E4DC] text-[#5A322A] hover:bg-[#F4EFEB]'
              }`}
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className={`lg:hidden border-t px-4 pt-3 pb-5 space-y-1 shadow-lg animate-fadeIn transition-colors ${
          isDark
            ? 'border-[#36415A] bg-[#202734]'
            : 'border-[#E8E4DC] bg-[#FAF8F5]'
        }`}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? isDark
                      ? 'bg-[#36415A] text-[#E0F8C7]'
                      : 'bg-[#5A322A] text-[#FAF8F5]'
                    : isDark
                      ? 'text-[#CBD5E1] hover:bg-[#273042]'
                      : 'text-[#5A322A] hover:bg-[#F3ECE8]'
                }`}
              >
                <Icon className={`w-4 h-4 ${
                  isActive 
                    ? isDark ? 'text-[#B7D894]' : 'text-[#E4A499]'
                    : isDark ? 'text-[#8FA0B8]' : 'text-[#BC7B6F]'
                }`} />
                {item.label}
              </button>
            );
          })}
          
          <div className="pt-3 border-t border-inherit mt-2 flex items-center justify-between text-xs px-2">
            <span className={isDark ? 'text-[#8FA0B8]' : 'text-[#826F6A]'}>FastAPI Backend (:8000)</span>
            <span className={apiHealthy ? (isDark ? 'text-[#B7D894]' : 'text-[#718A9E]') : 'text-[#BC7B6F]'}>
              {apiHealthy ? '● Online' : '○ Checking...'}
            </span>
          </div>

          <div className="pt-2 flex items-center justify-between text-xs px-2">
            <span className={isDark ? 'text-[#8FA0B8]' : 'text-[#826F6A]'}>Theme</span>
            <button
              onClick={toggleTheme}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                isDark
                  ? 'bg-[#273042] border-[#36415A] text-[#E0F8C7]'
                  : 'bg-[#FFFFFF] border-[#E8E4DC] text-[#5A322A]'
              }`}
            >
              {isDark ? <Moon className="w-3.5 h-3.5 text-[#B7D894]" /> : <Sun className="w-3.5 h-3.5 text-[#BC7B6F]" />}
              {isDark ? 'Dark Theme' : 'Light Theme'}
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
