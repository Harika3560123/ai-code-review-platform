import React, { useRef } from "react";
import Editor from "@monaco-editor/react";

export default function CodeEditor({
  code,
  onChange,
  language = "python",
  readOnly = false,
  highlightLine = null
}) {
  const editorRef = useRef(null);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
  };

  const getMonacoLanguage = (lang) => {
    switch (lang.toLowerCase()) {
      case "python":
        return "python";
      case "javascript":
        return "javascript";
      case "java":
        return "java";
      case "cpp":
      case "c":
        return "cpp";
      default:
        return "python";
    }
  };

  return (
    <div className="editor-container">
      <Editor
        height="450px"
        language={getMonacoLanguage(language)}
        value={code}
        theme="vs-dark"
        onChange={(val) => onChange && onChange(val || "")}
        onMount={handleEditorDidMount}
        options={{
          readOnly: readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
          lineNumbers: "on",
          roundedSelection: false,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 4,
          formatOnPaste: true,
          renderLineHighlight: "all",
        }}
        loading={
          <div className="editor-loading">
            <div className="spinner"></div>
            <span>Loading Code Editor...</span>
          </div>
        }
      />
    </div>
  );
}
