const sections = [
    { label: "Output",      href: "#production" },
    { label: "Employment",  href: "#employment" },
    { label: "Capacity",    href: "#capacity" },
    { label: "Orders",      href: "#orders" },
    { label: "Wages",       href: "#wages" },
    { label: "GDP",         href: "#gdp" },
    { label: "State Map",   href: "#map" },
  ];
  
  export function Sidebar() {
    return (
      <nav
        className="w-40 min-h-screen self-start p-4 flex flex-col gap-1 sticky top-0"
        style={{ background: "var(--card)" }}
      >
        <p className="text-xs font-bold uppercase tracking-widest mb-4" style={{ color: "var(--muted)" }}>
          Sections
        </p>
        {sections.map((s) => (
          <a
            key={s.href}
            href={s.href}
            className="text-sm py-1.5 px-2 rounded hover:bg-white/5 transition-colors"
            style={{ color: "var(--muted)" }}
          >
            {s.label}
          </a>
        ))}
      </nav>
    );
  }