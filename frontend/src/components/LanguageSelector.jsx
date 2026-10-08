import React from "react";

export default function LanguageSelector({ language, setLanguage, disabled = false }) {
  const languages = [
    { id: "python", label: "Python (Pylint, Bandit, AST)" },
    { id: "javascript", label: "JavaScript (ESLint, Syntax)" },
    { id: "java", label: "Java (Static, Security)" },
    { id: "cpp", label: "C / C++ (Static, Security)" }
  ];

  return (
    <div className="language-selector">
      <label htmlFor="lang-select">Language:</label>
      <select
        id="lang-select"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        disabled={disabled}
        className="select-input"
      >
        {languages.map((l) => (
          <option key={l.id} value={l.id}>
            {l.label}
          </option>
        ))}
      </select>
    </div>
  );
}
