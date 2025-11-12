import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type ComponentInfo = {
  title: string;
  description: string;
  details: string[];
};

const componentDetails: Record<string, ComponentInfo> = {
  user: {
    title: "User",
    description: "End users interact with the application through natural language",
    details: [
      "Ask questions like 'Show me all accounts' or 'Update this record'",
      "No need to know API syntax or database structure",
      "Conversational interface in the browser",
    ],
  },
  frontend: {
    title: "React Frontend",
    description: "Modern web interface for user interaction",
    details: [
      "Built with React and TypeScript",
      "Styled with Tailwind CSS",
      "Real-time chat interface",
      "Model selection and configuration",
      "Trace viewing for debugging",
    ],
  },
  databricksApp: {
    title: "Databricks Apps",
    description: "Hosting platform for the entire application",
    details: [
      "Hosts both frontend (React) and backend (FastAPI)",
      "Provides compute resources and networking",
      "Integrates with Databricks Secrets for secure credentials",
      "Automatic SSL and authentication",
      "Service Principal identity for secure API access",
    ],
  },
  agentLoop: {
    title: "AI Agent Loop",
    description: "Orchestrates multi-turn conversations with tool calling",
    details: [
      "Step 1: User question sent to Foundation Model",
      "Step 2: Model decides which tool(s) to call",
      "Step 3: Tools execute and return results",
      "Step 4: Model formats natural language response",
      "Can iterate multiple times for complex queries",
    ],
  },
  foundationModel: {
    title: "Databricks Foundation Model API",
    description: "Powerful LLMs accessible via API",
    details: [
      "Claude Sonnet 4 (default - best for reasoning)",
      "GPT-4o (OpenAI's latest)",
      "Llama 3.1 (Open source)",
      "Mixtral (Fast and efficient)",
      "Supports tool calling (function calling)",
    ],
  },
  tools: {
    title: "Dataverse Tools",
    description: "Six CRUD operations for Dataverse",
    details: [
      "list_tables - Discover available tables",
      "describe_table - Get schema/columns",
      "read_query - Query records with OData",
      "create_record - Insert new records",
      "update_record - Modify existing records",
      "delete_record - Remove records",
    ],
  },
  mcpProtocol: {
    title: "Model Context Protocol (MCP)",
    description: "Standardized protocol for LLM-to-data integration",
    details: [
      "Open standard by Anthropic",
      "Enables tools to expose capabilities to LLMs",
      "Standardizes request/response format",
      "Allows any MCP client to connect to this server",
      "Compatible with Claude Desktop, VS Code, and more",
    ],
  },
  auth: {
    title: "OAuth Authentication",
    description: "Secure connection to Dataverse using Service Principal",
    details: [
      "OAuth 2.0 Client Credentials flow",
      "Service Principal (App Registration in Azure AD)",
      "Credentials stored in Databricks Secrets",
      "Tokens automatically refreshed",
      "Principle of least privilege",
    ],
  },
  dataverse: {
    title: "Microsoft Dataverse",
    description: "Cloud database powering Dynamics 365",
    details: [
      "Relational database with business logic",
      "Powers Dynamics 365 Sales, Service, Marketing",
      "Web API v9.2 (REST)",
      "Stores entities like accounts, contacts, leads",
      "Enforces security roles and permissions",
    ],
  },
  dynamics: {
    title: "Dynamics 365",
    description: "Suite of business applications built on Dataverse",
    details: [
      "Sales - CRM and opportunity management",
      "Customer Service - Case and ticket management",
      "Marketing - Campaign and lead generation",
      "Field Service - Work order management",
      "All apps share the same Dataverse backend",
    ],
  },
};

export default function ArchitecturePage() {
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);

  const openDialog = (component: string) => {
    setSelectedComponent(component);
  };

  const closeDialog = () => {
    setSelectedComponent(null);
  };

  const currentInfo = selectedComponent ? componentDetails[selectedComponent] : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-auto">
      <div className="container mx-auto py-12 px-6 max-w-6xl">
        {/* Title */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
            Interactivity with Dynamics using AI
          </h1>
          <p className="text-2xl text-slate-400 font-light">
            Utilizing the Dataverse MCP server for enhanced agentic workflows
          </p>
          <p className="text-sm text-slate-500 mt-2">💡 Click on any component to learn more</p>
        </div>

        {/* Main Flow */}
        <div className="flex flex-col items-center gap-6">
          
          {/* User */}
          <button
            onClick={() => openDialog("user")}
            className="flex flex-col items-center hover:scale-105 transition-transform cursor-pointer"
          >
            <div className="w-24 h-24 bg-gradient-to-br from-slate-600 to-slate-700 rounded-full flex items-center justify-center shadow-xl hover:shadow-slate-500/30">
              <svg className="w-14 h-14 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="text-center mt-3">
              <p className="text-lg font-semibold">User</p>
              <p className="text-xs text-slate-500">Natural language questions</p>
            </div>
          </button>

          {/* Arrow Down */}
          <div className="text-4xl text-slate-600">↓</div>

          {/* Databricks Apps Container */}
          <div className="w-full max-w-5xl bg-slate-800/40 backdrop-blur border border-slate-600/50 rounded-3xl p-4 shadow-xl">
            <button
              onClick={() => openDialog("databricksApp")}
              className="w-full text-left hover:bg-slate-700/30 rounded-xl p-3 transition-colors mb-4"
            >
              <div className="flex items-center gap-3">
                {/* Databricks logo - simple brick representation */}
                <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-600 rounded-lg flex items-center justify-center">
                  <div className="grid grid-cols-2 gap-0.5 w-6 h-6">
                    <div className="bg-white rounded-sm"></div>
                    <div className="bg-white rounded-sm"></div>
                    <div className="bg-white rounded-sm"></div>
                    <div className="bg-white rounded-sm"></div>
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-200">Databricks Apps</h3>
                  <p className="text-xs text-slate-500">Hosting Platform</p>
                </div>
              </div>
            </button>

            {/* Frontend */}
            <button
              onClick={() => openDialog("frontend")}
              className="w-full bg-slate-700/30 hover:bg-slate-700/50 backdrop-blur border border-slate-600/30 rounded-xl p-4 mb-3 transition-colors text-left"
            >
              <div className="flex items-center gap-3">
                {/* React logo */}
                <div className="w-10 h-10 flex items-center justify-center">
                  <svg className="w-10 h-10" viewBox="-11.5 -10.23174 23 20.46348">
                    <circle cx="0" cy="0" r="2.05" fill="#61dafb"/>
                    <g stroke="#61dafb" strokeWidth="1" fill="none">
                      <ellipse rx="11" ry="4.2"/>
                      <ellipse rx="11" ry="4.2" transform="rotate(60)"/>
                      <ellipse rx="11" ry="4.2" transform="rotate(120)"/>
                    </g>
                  </svg>
                </div>
                <div>
                  <h4 className="text-lg font-semibold">React Frontend</h4>
                  <p className="text-sm text-slate-400">TypeScript + Tailwind CSS</p>
                </div>
              </div>
            </button>

            {/* Backend Box */}
            <div className="w-full bg-slate-700/40 backdrop-blur border border-slate-500/50 rounded-2xl p-6 shadow-xl">
              <div className="flex items-center gap-3 mb-6">
                {/* FastAPI logo simplified */}
                <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-emerald-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">FA</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold">FastAPI Backend</h3>
                  <p className="text-sm text-slate-400">Python API Server + AI Agent</p>
                </div>
              </div>

              <div className="space-y-4">
                {/* AI Agent Loop */}
                <button
                  onClick={() => openDialog("agentLoop")}
                  className="w-full bg-indigo-900/20 hover:bg-indigo-900/30 rounded-xl p-5 border border-indigo-700/30 transition-colors text-left"
                >
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 7H7v6h6V7z"/>
                      <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd"/>
                    </svg>
                    AI Agent Loop
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="flex flex-col items-center text-center">
                      <div className="w-10 h-10 bg-indigo-600/60 rounded-full flex items-center justify-center font-bold text-sm mb-2">1</div>
                      <p className="text-xs">Question to Model</p>
                    </div>
                    <div className="flex flex-col items-center text-center">
                      <div className="w-10 h-10 bg-indigo-600/60 rounded-full flex items-center justify-center font-bold text-sm mb-2">2</div>
                      <p className="text-xs">Tool Selection</p>
                    </div>
                    <div className="flex flex-col items-center text-center">
                      <div className="w-10 h-10 bg-indigo-600/60 rounded-full flex items-center justify-center font-bold text-sm mb-2">3</div>
                      <p className="text-xs">Execute & Return</p>
                    </div>
                    <div className="flex flex-col items-center text-center">
                      <div className="w-10 h-10 bg-indigo-600/60 rounded-full flex items-center justify-center font-bold text-sm mb-2">4</div>
                      <p className="text-xs">Natural Response</p>
                    </div>
                  </div>
                </button>

                {/* Foundation Models */}
                <button
                  onClick={() => openDialog("foundationModel")}
                  className="w-full bg-emerald-900/20 hover:bg-emerald-900/30 rounded-xl p-5 border border-emerald-700/30 transition-colors text-left"
                >
                  <h4 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-red-500 to-orange-600 rounded flex items-center justify-center">
                      <span className="text-white font-bold text-xs">DB</span>
                    </div>
                    Databricks Foundation Model API
                  </h4>
                  <p className="text-sm text-slate-300">Powered by industry-leading LLMs</p>
                </button>

                {/* Tools */}
                <button
                  onClick={() => openDialog("tools")}
                  className="w-full bg-amber-900/20 hover:bg-amber-900/30 rounded-xl p-5 border border-amber-700/30 transition-colors text-left"
                >
                  <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd"/>
                    </svg>
                    Available Tools
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    <div className="bg-slate-600/40 px-3 py-2 rounded-lg text-xs font-medium">
                      List Tables
                    </div>
                    <div className="bg-slate-600/40 px-3 py-2 rounded-lg text-xs font-medium">
                      Describe Table
                    </div>
                    <div className="bg-slate-600/40 px-3 py-2 rounded-lg text-xs font-medium">
                      Read Query
                    </div>
                    <div className="bg-slate-600/40 px-3 py-2 rounded-lg text-xs font-medium">
                      Create Record
                    </div>
                    <div className="bg-slate-600/40 px-3 py-2 rounded-lg text-xs font-medium">
                      Update Record
                    </div>
                    <div className="bg-slate-600/40 px-3 py-2 rounded-lg text-xs font-medium">
                      Delete Record
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </div>

          {/* Arrow Down */}
          <div className="text-4xl text-slate-600">↓</div>

          {/* MCP Protocol Layer */}
          <button
            onClick={() => openDialog("mcpProtocol")}
            className="w-full max-w-3xl bg-slate-700/30 hover:bg-slate-700/50 backdrop-blur border border-slate-600/40 rounded-xl p-5 shadow-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
                </svg>
              </div>
              <div className="text-left">
                <h4 className="text-lg font-semibold">Model Context Protocol (MCP)</h4>
                <p className="text-sm text-slate-400">Standardized LLM-to-data integration protocol</p>
              </div>
            </div>
          </button>

          {/* Arrow Down */}
          <div className="text-4xl text-slate-600">↓</div>

          {/* Authentication */}
          <button
            onClick={() => openDialog("auth")}
            className="w-full max-w-2xl bg-slate-700/30 hover:bg-slate-700/50 backdrop-blur border border-slate-600/40 rounded-xl p-5 shadow-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd"/>
                </svg>
              </div>
              <div className="text-left">
                <h4 className="text-lg font-semibold">Secure Authentication</h4>
                <p className="text-sm text-slate-400">OAuth 2.0 Service Principal via Databricks Secrets</p>
              </div>
            </div>
          </button>

          {/* Arrow Down */}
          <div className="text-4xl text-slate-600">↓</div>

          {/* Dataverse & Dynamics Container */}
          <div className="w-full max-w-4xl bg-slate-800/40 backdrop-blur border border-slate-600/50 rounded-3xl p-6 shadow-xl">
            {/* Dataverse */}
            <button
              onClick={() => openDialog("dataverse")}
              className="w-full flex items-center gap-4 hover:bg-slate-700/30 rounded-xl p-4 transition-colors mb-4"
            >
              {/* Microsoft Dataverse logo representation */}
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 12v3c0 1.657 3.134 3 7 3s7-1.343 7-3v-3c0 1.657-3.134 3-7 3s-7-1.343-7-3z"/>
                  <path d="M3 7v3c0 1.657 3.134 3 7 3s7-1.343 7-3V7c0 1.657-3.134 3-7 3S3 8.657 3 7z"/>
                  <path d="M17 5c0 1.657-3.134 3-7 3S3 6.657 3 5s3.134-3 7-3 7 1.343 7 3z"/>
                </svg>
              </div>
              <div className="text-left">
                <p className="text-xl font-semibold">Microsoft Dataverse</p>
                <p className="text-sm text-slate-400">Unified data platform with Web API v9.2</p>
              </div>
            </button>

            {/* Dynamics 365 */}
            <button
              onClick={() => openDialog("dynamics")}
              className="w-full bg-slate-700/30 hover:bg-slate-700/50 backdrop-blur border border-slate-600/30 rounded-xl p-5 transition-colors text-left"
            >
              <div className="flex items-center gap-3">
                {/* Dynamics 365 logo representation */}
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">D365</span>
                </div>
                <div>
                  <h4 className="text-lg font-semibold">Dynamics 365</h4>
                  <p className="text-sm text-slate-400">Sales • Service • Marketing • Field Service</p>
                </div>
              </div>
            </button>
          </div>

        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-slate-600 text-sm">
          <p>© 2025 Databricks Inc. — All rights reserved</p>
        </div>
      </div>

      {/* Dialog */}
      <Dialog open={!!selectedComponent} onOpenChange={closeDialog}>
        <DialogContent className="bg-slate-800 text-white border-slate-700 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-slate-100">
              {currentInfo?.title}
            </DialogTitle>
            <DialogDescription className="text-slate-300 text-base mt-2">
              {currentInfo?.description}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            <h4 className="text-sm font-semibold text-slate-400 uppercase mb-3">Key Details</h4>
            <ul className="space-y-2">
              {currentInfo?.details.map((detail, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="text-slate-400 mt-1">✓</span>
                  <span className="text-slate-200">{detail}</span>
                </li>
              ))}
            </ul>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
