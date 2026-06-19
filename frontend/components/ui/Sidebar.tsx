"use client";

const sections = [
  { label: "Output",      href: "#production" },
  { label: "Employment",  href: "#employment" },
  { label: "Capacity",    href: "#capacity" },
  { label: "Orders",      href: "#orders" },
  { label: "Wages",       href: "#wages" },
  { label: "GDP",         href: "#gdp" },
  { label: "State Map",   href: "#map" },
  { label: "Summary",     href: "#summary" },
];

export function Sidebar() {
  function handleClick(e: React.MouseEvent<HTMLAnchorElement>, href: string) {
    e.preventDefault();
    document.querySelector(href)?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  return (
    <nav
      className="w-full lg:w-40 lg:min-h-screen lg:self-start p-3 lg:p-4 flex flex-row lg:flex-col gap-1 overflow-x-auto lg:overflow-x-visible sticky top-0 z-10"
      style={{ background: "var(--card)" }}
    >
      <p className="hidden lg:block text-xs font-bold uppercase tracking-widest mb-4" style={{ color: "var(--muted)" }}>
        Sections
      </p>
      {sections.map((s) => (
        <a
          key={s.href}
          href={s.href}
          onClick={(e) => handleClick(e, s.href)}
          className="text-sm py-1.5 px-2 rounded hover:bg-white/5 transition-colors whitespace-nowrap shrink-0"
          style={{ color: "var(--muted)" }}
        >
          {s.label}
        </a>
      ))}
    </nav>
  );
}
