import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Send,
  Loader2,
  Sparkles,
  Activity,
  Copy,
  Check,
  Bot,
  User,
  HelpCircle,
} from "lucide-react";
import { useTheme } from "@/components/theme-provider";
import DOMPurify from "dompurify";
import { marked } from "marked";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface Model {
  id: string;
  name: string;
  provider: string;
  supports_tools: boolean;
  context_window: number;
  type: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  tool_calls?: Array<{
    tool: string;
    args: any;
    result: any;
  }>;
  trace_id?: string;
}

interface ChatPageAgentProps {
  onViewTrace?: (traceId: string) => void;
}

export function ChatPageAgent({ onViewTrace }: ChatPageAgentProps) {
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [showHelp, setShowHelp] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { theme } = useTheme();

  const isDark = theme === "dark";

  useEffect(() => {
    fetchModels();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchModels = async () => {
    try {
      const response = await fetch("/api/chat/models");
      const data = await response.json();
      setModels(data.models || []);
      setSelectedModel(data.default || "");
    } catch (error) {
      console.error("Failed to fetch models:", error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading || !selectedModel) return;

    const userMessage: Message = {
      role: "user",
      content: input,
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      // Call the agent chat API
      const response = await fetch("/api/agent/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: newMessages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
          model: selectedModel,
          max_tokens: 2048,
          temperature: 0.7,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      // Add assistant response
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "I apologize, but I couldn't generate a response.",
        tool_calls: data.tool_calls,
        trace_id: data.trace_id,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyMessage = (content: string, index: number) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const renderMarkdown = (content: string) => {
    const html = marked.parse(content) as string;
    const sanitized = DOMPurify.sanitize(html);
    return { __html: sanitized };
  };

  return (
    <div
      className={`flex flex-col h-full ${
        isDark ? "bg-[#1C3D42]" : "bg-gray-50"
      }`}
    >
      {/* Top Bar with Model Selection */}
      <div
        className={`flex items-center justify-between px-6 py-3 ${
          isDark ? "bg-[#16343A]" : "bg-white"
        } border-b ${isDark ? "border-white/10" : "border-gray-200"}`}
      >
        <div className="flex items-center gap-2">
          <Sparkles className={`h-5 w-5 ${isDark ? "text-blue-400" : "text-blue-600"}`} />
          <span className={`font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>
            Dataverse MCP Chat
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className={`text-sm ${isDark ? "text-gray-400" : "text-gray-600"}`}>
              Model:
            </span>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger
                className={`w-[280px] ${
                  isDark
                    ? "bg-white/5 border-white/10 text-white"
                    : "bg-gray-50 border-gray-300 text-gray-900"
                }`}
              >
                <SelectValue placeholder="Select a model">
                  {models.find((m) => m.id === selectedModel)?.name || "No model selected"}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {models.length === 0 ? (
                  <div className="p-4 text-center text-sm text-muted-foreground">
                    No models configured
                  </div>
                ) : (
                  models.map((model) => (
                    <SelectItem
                      key={model.id}
                      value={model.id}
                      disabled={!model.supports_tools}
                    >
                      <div className="flex flex-col">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-medium ${
                              !model.supports_tools ? "text-muted-foreground" : ""
                            }`}
                          >
                            {model.name}
                          </span>
                          {!model.supports_tools && (
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground border border-border">
                              Not tool-enabled
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {model.provider} • {model.context_window.toLocaleString()} tokens
                        </span>
                      </div>
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          /* Empty State */
          <div className="flex flex-col items-center justify-center h-full">
            <div className="max-w-2xl w-full space-y-6 text-center">
              <div className="space-y-4">
                <h1
                  className={`text-5xl font-bold ${
                    isDark ? "text-white" : "text-gray-900"
                  }`}
                >
                  What can I help you with today?
                </h1>
                <p
                  className={`text-lg ${
                    isDark ? "text-white/80" : "text-gray-600"
                  }`}
                >
                  I can help you explore and interact with your Microsoft Dataverse data
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* Conversation View */
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-4 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      isDark ? "bg-blue-500/20" : "bg-blue-100"
                    }`}
                  >
                    <Bot className="h-4 w-4 text-blue-500" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                    message.role === "user"
                      ? "bg-blue-500 text-white"
                      : isDark
                      ? "bg-white/10 text-white border border-white/20"
                      : "bg-white text-gray-900 border border-gray-200"
                  }`}
                >
                  <div
                    className="prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={renderMarkdown(message.content)}
                  />
                  
                  {/* Tool Calls */}
                  {message.tool_calls && message.tool_calls.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {message.tool_calls.map((toolCall, tcIndex) => (
                        <span
                          key={tcIndex}
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                            message.role === "user"
                              ? "bg-white/20"
                              : isDark
                              ? "bg-blue-500/20 text-blue-300"
                              : "bg-blue-100 text-blue-700"
                          }`}
                        >
                          <Sparkles className="h-3 w-3" />
                          {toolCall.tool}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Trace Link */}
                  {message.trace_id && onViewTrace && (
                    <button
                      onClick={() => onViewTrace(message.trace_id!)}
                      className={`mt-2 flex items-center gap-1 text-xs ${
                        message.role === "user"
                          ? "text-white/80 hover:text-white"
                          : isDark
                          ? "text-blue-400 hover:text-blue-300"
                          : "text-blue-600 hover:text-blue-700"
                      }`}
                    >
                      <Activity className="h-3 w-3" />
                      View Trace
                    </button>
                  )}

                  {/* Copy Button */}
                  {message.role === "assistant" && (
                    <button
                      onClick={() => copyMessage(message.content, index)}
                      className={`mt-2 flex items-center gap-1 text-xs ${
                        isDark
                          ? "text-gray-400 hover:text-white"
                          : "text-gray-500 hover:text-gray-900"
                      }`}
                    >
                      {copiedIndex === index ? (
                        <>
                          <Check className="h-3 w-3" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3" />
                          Copy
                        </>
                      )}
                    </button>
                  )}
                </div>
                {message.role === "user" && (
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      "bg-blue-500"
                    }`}
                  >
                    <User className="h-4 w-4 text-white" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-4 justify-start">
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    isDark ? "bg-blue-500/20" : "bg-blue-100"
                  }`}
                >
                  <Bot className="h-4 w-4 text-blue-500" />
                </div>
                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                    isDark
                      ? "bg-white/10 border border-white/20"
                      : "bg-white border border-gray-200"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Bottom Input */}
      <div
        className={`p-4 ${
          isDark ? "bg-[#16343A]" : "bg-white"
        } border-t ${isDark ? "border-white/10" : "border-gray-200"}`}
      >
        <div className="max-w-4xl mx-auto relative">
          <Textarea
            ref={textareaRef}
            placeholder="Ask me about your Dataverse data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className={`min-h-[80px] pr-14 resize-none ${
              isDark
                ? "bg-white/5 border-white/10 text-white placeholder:text-white/60"
                : "bg-gray-50 border-gray-300 text-gray-900 placeholder:text-gray-500"
            }`}
            disabled={loading}
          />
          <Button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            size="icon"
            className="absolute bottom-3 right-3 rounded-full bg-blue-500 hover:bg-blue-600 text-white"
          >
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>

      {/* User Guide Button - Bottom Left Corner */}
      <Dialog open={showHelp} onOpenChange={setShowHelp}>
        <DialogTrigger asChild>
          <Button
            className={`fixed bottom-6 left-6 rounded-full shadow-lg ${
              isDark
                ? "bg-white/10 hover:bg-white/20 text-white border border-white/20"
                : "bg-white hover:bg-gray-50 text-gray-900 border border-gray-200"
            }`}
            size="lg"
          >
            <HelpCircle className="h-5 w-5 mr-2" />
            User Guide
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl">Dataverse MCP Server</DialogTitle>
            <DialogDescription>
              Model Context Protocol tools for Microsoft Dataverse
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6 py-4">
            {/* Example Prompts */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                💬 Example Prompts
              </h3>
              <ul className="space-y-2 text-sm">
                <li className="ml-4">• "List all tables in my Dataverse environment"</li>
                <li className="ml-4">• "Show me the schema for the Account table"</li>
                <li className="ml-4">• "Query the Contact table for all active contacts"</li>
                <li className="ml-4">• "Create a new account record with name 'Contoso'"</li>
                <li className="ml-4">• "Update contact record with ID xyz123"</li>
              </ul>
            </div>

            {/* Available Tools */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                🔧 Available Tools
              </h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-semibold text-sm mb-1">list_tables</h4>
                  <p className="text-sm text-muted-foreground ml-4">
                    Browse and discover all available Dataverse tables in your environment
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-sm mb-1">describe_table</h4>
                  <p className="text-sm text-muted-foreground ml-4">
                    Get detailed schema information, column types, and metadata for a specific table
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-sm mb-1">read_query</h4>
                  <p className="text-sm text-muted-foreground ml-4">
                    Query Dataverse data using FetchXML to retrieve records matching your criteria
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-sm mb-1">create_record</h4>
                  <p className="text-sm text-muted-foreground ml-4">
                    Create new records in Dataverse tables with specified field values
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-sm mb-1">update_record</h4>
                  <p className="text-sm text-muted-foreground ml-4">
                    Update existing Dataverse records by ID with new field values
                  </p>
                </div>
              </div>
            </div>

            {/* Configuration Info */}
            <div className={`p-4 rounded-lg ${
              isDark ? "bg-blue-500/10 border border-blue-500/20" : "bg-blue-50 border border-blue-200"
            }`}>
              <h3 className="text-sm font-semibold mb-2">ℹ️ Configuration</h3>
              <p className="text-sm text-muted-foreground">
                This MCP server connects to your Microsoft Dataverse environment using Service Principal authentication. 
                All operations are performed through the Dataverse Web API.
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
