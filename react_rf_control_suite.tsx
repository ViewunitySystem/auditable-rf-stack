import React, { useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Activity, Antenna, BarChart3, Binary, Cable, CheckCircle2,ChevronDown, PauseCircle, PlayCircle,
  Download, Gauge, Globe2, History, Link2, Lock, LogOut, Radio, Settings, ShieldCheck, SignalHigh, Upload, Wand2
} from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip as RTooltip, XAxis, YAxis } from "recharts";

// --- Web Serial API types ---
interface SerialPort {
  readable: ReadableStream<Uint8Array> | null;
  writable: WritableStream<Uint8Array> | null;
  open(options: { baudRate: number }): Promise<void>;
  close(): Promise<void>;
}


// --- live data containers (no mock/random) ---
type SpectrumPoint = { f: number; p: number };
type TpPoint = { t: number; mbps: number };

// NOTE: Arrays are seeded empty and filled by real telemetry (Web Serial or provided API).
// UI/UX is unchanged; only data plumbing is added.

// helper UI chip
const Chip = ({ children }: { children: React.ReactNode }) => (
  <span className="text-xs px-2 py-1 rounded-full bg-muted/50 border border-border">{children}</span>
);

// reusable small metric card
const Metric = ({ label, value, hint }: { label: string; value: string; hint?: string }) => (
  <div className="flex flex-col gap-1">
    <div className="text-xs text-muted-foreground">{label}</div>
    <div className="text-lg font-semibold tracking-tight">{value}</div>
    {hint && <div className="text-[10px] text-muted-foreground">{hint}</div>}
  </div>
);

export default function RFControlSuite() {
  const [connected, setConnected] = useState(false);
  const [band, setBand] = useState("B3");
  const [spectrum, setSpectrum] = useState<SpectrumPoint[]>([]);
  const [throughput, setThroughput] = useState<TpPoint[]>([]);
  const serialPortRef = useRef<SerialPort | null>(null);
  const serialReaderAbort = useRef<AbortController | null>(null);
  const [power, setPower] = useState([20]); // dBm
  const [txOn, setTxOn] = useState(false);
  const [ca, setCA] = useState(["B1","B3","B7","B20"]);
  const [profile, setProfile] = useState("Urban");
  const [logOpen, setLogOpen] = useState(false);

  const caLabel = useMemo(()=> ca.join(" + "),[ca]);

  return (
    <TooltipProvider>
      <div className="min-h-screen w-full bg-gradient-to-b from-background to-muted/30">
        {/* header */}
        <div className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-background/70 border-b">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="p-2 rounded-2xl bg-primary/10">
                <Radio className="h-5 w-5"/>
              </motion.div>
              <div>
                <div className="font-semibold leading-tight">RF Control Suite</div>
                <div className="text-xs text-muted-foreground">Software-defined RF / SDR • 433 MHz – 6 GHz</div>
              </div>
              <Badge variant={connected?"default":"secondary"} className="ml-2">{connected?"Connected":"Disconnected"}</Badge>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={async ()=>{
                  if (!connected) {
                    // Try Web Serial first; if unavailable, fall back to WebSocket (ws://localhost:8765/telemetry).
                    try {
                      // @ts-ignore: lib.dom.d.ts gated behind flag in some toolchains
                      if (("serial" in navigator)) {
                        // @ts-ignore
                        const port: SerialPort = await (navigator as any).serial.requestPort();
                        await port.open({ baudRate: 115200 });
                        serialPortRef.current = port;
                        serialReaderAbort.current = new AbortController();

                        const readable = port.readable?.pipeThrough(new TextDecoderStream() as any);
                        const reader = readable?.getReader();

                        (async () => {
                          let t = 0; let buffer = "";
                          try {
                            while (reader) {
                              const { value, done } = await reader.read();
                              if (done) break; if (!value) continue;
                              buffer += value;
                              let idx;
                              while ((idx = buffer.indexOf("\n")) !== -1) {
                                const line = buffer.slice(0, idx).trim();
                                buffer = buffer.slice(idx + 1);
                                if (!line) continue;
                                try {
                                  const msg = JSON.parse(line);
                                  if (typeof msg.mbps === "number") {
                                    t += 1;
                                    setThroughput(prev => {
                                      const next = [...prev, { t, mbps: msg.mbps }];
                                      return next.length > 300 ? next.slice(-300) : next;
                                    });
                                  }
                                  if (typeof msg.f === "number" && typeof msg.p === "number") {
                                    setSpectrum(prev => {
                                      const fMHz = msg.f > 1e4 ? msg.f / 1e6 : msg.f;
                                      const map = new Map(prev.map(p => [p.f, p.p]));
                                      map.set(Number(fMHz.toFixed(3)), msg.p);
                                      const arr = Array.from(map.entries()).map(([f, p]) => ({ f: Number(f), p }));
                                      arr.sort((a,b)=>a.f-b.f);
                                      return arr.slice(-1024);
                                    });
                                  }
                                } catch {}
                              }
                            }
                          } catch {}
                        })();

                        setConnected(true);
                      } else {
                        // WebSocket fallback (no UI changes)
                        const ws = new WebSocket("ws://localhost:8765/telemetry");
                        (window as any).__rf_ws__ = ws;
                        ws.onmessage = (ev) => {
                          try {
                            const msg = JSON.parse(ev.data);
                            if (typeof msg.mbps === "number") {
                              setThroughput(prev => {
                                const t = prev.length ? prev[prev.length-1].t + 1 : 1;
                                const next = [...prev, { t, mbps: msg.mbps }];
                                return next.length > 300 ? next.slice(-300) : next;
                              });
                            }
                            if (typeof msg.f === "number" && typeof msg.p === "number") {
                              setSpectrum(prev => {
                                const fMHz = msg.f > 1e4 ? msg.f / 1e6 : msg.f;
                                const map = new Map(prev.map(p => [p.f, p.p]));
                                map.set(Number(fMHz.toFixed(3)), msg.p);
                                const arr = Array.from(map.entries()).map(([f, p]) => ({ f: Number(f), p }));
                                arr.sort((a,b)=>a.f-b.f);
                                return arr.slice(-1024);
                              });
                            }
                          } catch {}
                        };
                        ws.onopen = () => setConnected(true);
                        ws.onclose = () => setConnected(false);
                      }
                    } catch (e) {
                      console.error(e);
                      setConnected(false);
                    }
                  } else {
                    // disconnect
                    try {
                      serialReaderAbort.current?.abort();
                    } catch {}
                    try {
                      await serialPortRef.current?.close();
                    } catch {}
                    serialPortRef.current = null;
                    try {
                      const ws: WebSocket | undefined = (window as any).__rf_ws__;
                      ws?.close();
                      (window as any).__rf_ws__ = undefined;
                    } catch {}
                    setConnected(false);
                  }
                }}
              >
                {connected? <LogOut className="h-4 w-4 mr-2"/> : <Link2 className="h-4 w-4 mr-2"/>}
                {connected?"Disconnect":"Connect"}
              </Button>
              <Dialog open={logOpen} onOpenChange={setLogOpen}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm"><History className="h-4 w-4 mr-2"/>Logs</Button>
                </DialogTrigger>
                <DialogContent className="max-w-3xl">
                  <DialogHeader>
                    <DialogTitle>Event Log</DialogTitle>
                    <DialogDescription>Runtime events, API calls, compliance checks.</DialogDescription>
                  </DialogHeader>
                  <div className="h-72 overflow-auto text-sm font-mono space-y-1">
                    {Array.from({length:24}).map((_,i)=> (
                      <div key={i} className="flex items-center gap-2">
                        <span className="text-muted-foreground">[{new Date().toLocaleTimeString()}]</span>
                        <span>INFO</span>
                        <span>CA={caLabel} • Band={band} • TX={txOn?"ON":"OFF"}</span>
                      </div>
                    ))}
                  </div>
                </DialogContent>
              </Dialog>
              <Button size="sm"><Download className="h-4 w-4 mr-2"/>Export</Button>
              <Button size="sm" variant="outline"><Settings className="h-4 w-4 mr-2"/>Settings</Button>
            </div>
          </div>
        </div>

        {/* main */}
        <div className="max-w-7xl mx-auto px-4 py-6">
          <Tabs defaultValue="dashboard" className="w-full">
            <TabsList className="grid grid-cols-4 lg:grid-cols-8">
              <TabsTrigger value="dashboard"><Gauge className="h-4 w-4 mr-2"/>Dashboard</TabsTrigger>
              <TabsTrigger value="bands"><SignalHigh className="h-4 w-4 mr-2"/>Bänder</TabsTrigger>
              <TabsTrigger value="ca"><Activity className="h-4 w-4 mr-2"/>Carrier Agg.</TabsTrigger>
              <TabsTrigger value="sdr"><BarChart3 className="h-4 w-4 mr-2"/>SDR</TabsTrigger>
              <TabsTrigger value="antenna"><Antenna className="h-4 w-4 mr-2"/>Antenne</TabsTrigger>
              <TabsTrigger value="api"><Globe2 className="h-4 w-4 mr-2"/>APIs</TabsTrigger>
              <TabsTrigger value="compliance"><ShieldCheck className="h-4 w-4 mr-2"/>Compliance</TabsTrigger>
              <TabsTrigger value="tools"><Wand2 className="h-4 w-4 mr-2"/>Tools</TabsTrigger>
            </TabsList>

            {/* DASHBOARD */}
            <TabsContent value="dashboard" className="mt-6 space-y-6">
              <div className="grid md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center"><Gauge className="h-4 w-4 mr-2"/>Live Throughput</CardTitle>
                    <CardDescription>Aggregated downlink (Mbps)</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-40">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={throughput} margin={{ left: 8, right: 8, top: 10, bottom: 0 }}>
                          <defs>
                            <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="currentColor" stopOpacity={0.3}/>
                              <stop offset="95%" stopColor="currentColor" stopOpacity={0.0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid vertical={false} className="stroke-muted"/>
                          <XAxis dataKey="t" tickLine={false} axisLine={false} fontSize={12}/>
                          <YAxis dataKey="mbps" tickLine={false} axisLine={false} fontSize={12}/>
                          <RTooltip cursor={false} />
                          <Area type="monotone" dataKey="mbps" stroke="currentColor" fill="url(#g1)" strokeWidth={2} />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                  <CardFooter className="justify-between">
                    <Metric label="Aktiv" value={txOn?"TX/RX":"RX"} />
                    <Metric label="CA" value={`${ca.length}CA`} hint={caLabel} />
                    <Metric label="Band" value={band} />
                  </CardFooter>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center"><BarChart3 className="h-4 w-4 mr-2"/>Spektrum</CardTitle>
                    <CardDescription>RF-Pegel (dBm)</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-40">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={spectrum} margin={{ left: 8, right: 8, top: 10, bottom: 0 }}>
                          <CartesianGrid vertical={false} className="stroke-muted"/>
                          <XAxis dataKey="f" tickLine={false} axisLine={false} fontSize={12} tickFormatter={(v)=>`${v} MHz`}/>
                          <YAxis dataKey="p" tickLine={false} axisLine={false} fontSize={12}/>
                          <RTooltip cursor={false} />
                          <Area type="monotone" dataKey="p" stroke="currentColor" fillOpacity={0.2} fill="currentColor" strokeWidth={2} />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                  <CardFooter className="justify-between">
                    <Metric label="Min" value="-118 dBm" />
                    <Metric label="Max" value="-72 dBm" />
                    <Metric label="Noise" value="-95 dBm" />
                  </CardFooter>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center"><ShieldCheck className="h-4 w-4 mr-2"/>Compliance</CardTitle>
                    <CardDescription>Regel- & Audit-Status</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Tx-Freigabe (Band {band})</span>
                      <Badge variant="secondary">Auto-Check</Badge>
                    </div>
                    <Progress value={72} />
                    <Alert>
                      <ShieldCheck className="h-4 w-4" />
                      <AlertTitle>Audit aktiv</AlertTitle>
                      <AlertDescription>Alle Operationen werden auf einer unveränderlichen Kette geloggt.</AlertDescription>
                    </Alert>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><Activity className="h-4 w-4 mr-2"/>Schnellsteuerung</CardTitle>
                  <CardDescription>Verbinden • Band • Leistung • TX</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-4 gap-4">
                  <div>
                    <Label className="text-xs">Band</Label>
                    <Select value={band} onValueChange={setBand}>
                      <SelectTrigger><SelectValue placeholder="Band"/></SelectTrigger>
                      <SelectContent className="max-h-64">
                        {(["B1","B3","B7","B8","B20","B28","n78"])?.map(b => (
                          <SelectItem key={b} value={b}>{b}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-xs">Sendeleistung ({power[0]} dBm)</Label>
                    <Slider value={power} onValueChange={setPower} min={0} max={24} step={1} className="mt-2"/>
                  </div>
                  <div>
                    <Label className="text-xs">TX</Label>
                    <div className="flex items-center gap-3 mt-2">
                      <Switch checked={txOn} onCheckedChange={setTxOn}/>
                      <Chip>{txOn?"ON":"OFF"}</Chip>
                    </div>
                  </div>
                  <div className="flex items-end">
                    <Button className="w-full" variant={txOn?"destructive":"default"}>
                      {txOn? <PauseCircle className="h-4 w-4 mr-2"/> : <PlayCircle className="h-4 w-4 mr-2"/>}
                      {txOn?"Stop TX":"Start TX"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* BANDS */}
            <TabsContent value="bands" className="mt-6 space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><SignalHigh className="h-4 w-4 mr-2"/>Band-Manager</CardTitle>
                  <CardDescription>Aktivierung/Whitelist, Scanmodi, Gerätekonfiguration</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-3">
                    <Label>Scanmodus</Label>
                    <Select defaultValue="all">
                      <SelectTrigger><SelectValue/></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Alle Standards</SelectItem>
                        <SelectItem value="lte">LTE/NR only</SelectItem>
                        <SelectItem value="legacy">GSM/UMTS only</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="border rounded-2xl p-3">
                      <div className="text-xs text-muted-foreground mb-2">Whitelist</div>
                      <div className="grid grid-cols-3 gap-2">
                        {Array.from({length:15}).map((_,i)=> (
                          <div key={i} className="flex items-center gap-2">
                            <Checkbox id={`b-${i}`}/>
                            <label htmlFor={`b-${i}`} className="text-xs">B{[1,3,7,8,20,28,32,38,40,41,42,48,66,71,75][i]}</label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Label>AT / QCFG</Label>
                    <div className="grid gap-2">
                      <Input defaultValue='AT+QCFG="band",0,0,0x800C0'/>
                      <Input defaultValue='AT+QCFG="CA_COMBINATION","B1+B3+B7+B20"'/>
                      <Input defaultValue='AT+QCFG="nwscanmode",7'/>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={()=>{
                        // When connected via Web Serial, forward the AT commands line-by-line to the device
                        (async () => {
                          try {
                            const port = serialPortRef.current;
                            const inputs = Array.from((document.querySelectorAll('input[data-at]') as NodeListOf<HTMLInputElement>) || []);
                            const cmds = inputs.map(el => el.value.trim()).filter(Boolean);
                            if (port && port.writable) {
                              const encoder = new TextEncoder();
                              const writer = port.writable.getWriter();
                              for (const cmd of cmds) {
                                await writer.write(encoder.encode(cmd + "\r\n"));
                              }
                              writer.releaseLock();
                            } else {
                              const ws: WebSocket | undefined = (window as any).__rf_ws__;
                              if (ws && ws.readyState === ws.OPEN) {
                                ws.send(JSON.stringify({ cmds }));
                              }
                            }
                          } catch (e) {
                            console.error(e);
                          }
                        })();
                      }}><Upload className="h-4 w-4 mr-2"/>Senden</Button>
                      <Button size="sm" variant="outline"><Download className="h-4 w-4 mr-2"/>Lesen</Button>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Label>Profile</Label>
                    <Select value={profile} onValueChange={setProfile}>
                      <SelectTrigger><SelectValue/></SelectTrigger>
                      <SelectContent>
                        {["Urban","Rural","Indoor","LEO"].map(p => (
                          <SelectItem key={p} value={p}>{p}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <Metric label="DL Cap" value="600+ Mbps"/>
                      <Metric label="UL Cap" value="120 Mbps"/>
                      <Metric label="RX Chains" value="4"/>
                      <Metric label="TX Chains" value="1"/>
                    </div>
                    <Button variant="secondary"><Binary className="h-4 w-4 mr-2"/>Speichern</Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* CA */}
            <TabsContent value="ca" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><Activity className="h-4 w-4 mr-2"/>Carrier Aggregation</CardTitle>
                  <CardDescription>Konfiguration & Validierung</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <Label>Combo</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {["B1","B3","B7","B8","B20","B28"].map(b => (
                        <Button
                          key={b}
                          variant={ca.includes(b) ? "default" : "outline"}
                          onClick={() => setCA(prev => (prev.includes(b) ? prev.filter(x => x !== b) : [...prev, b]))}
                        >
                          {b}
                        </Button>
                      ))}
                    </div>
                    <div className="text-sm">Aktiv: <Badge>{caLabel}</Badge></div>
                    <Button><Upload className="h-4 w-4 mr-2"/>Anwenden</Button>
                  </div>
                  <div className="space-y-3">
                    <Label>Validierung</Label>
                    <Collapsible>
                      <CollapsibleTrigger className="flex items-center gap-2 text-sm"><ChevronDown className="h-4 w-4"/>Bedingungen</CollapsibleTrigger>
                      <CollapsibleContent className="text-xs text-muted-foreground mt-2">
                        Prüft Band-Support, Duplex-Modus, MIMO-Ketten, Netz-Features, und regulatorische Limits.
                      </CollapsibleContent>
                    </Collapsible>
                    <div className="grid grid-cols-2 gap-2">
                      <Alert>
                        <CheckCircle2 className="h-4 w-4" />
                        <AlertTitle>Kombination zulässig</AlertTitle>
                        <AlertDescription>Alle Bänder kompatibel; Gerät unterstützt 4CA.</AlertDescription>
                      </Alert>
                      <Alert>
                        <Lock className="h-4 w-4" />
                        <AlertTitle>Regionale Limitierung</AlertTitle>
                        <AlertDescription>TX-Whitelist erforderlich, bevor gesendet wird.</AlertDescription>
                      </Alert>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* SDR */}
            <TabsContent value="sdr" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><BarChart3 className="h-4 w-4 mr-2"/>SDR Monitor</CardTitle>
                  <CardDescription>433/868/915 MHz, L/S/C-Band</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <div className="h-56">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={spectrum} margin={{ left: 8, right: 8, top: 10, bottom: 0 }}>
                          <CartesianGrid vertical={false} className="stroke-muted"/>
                          <XAxis dataKey="f" tickLine={false} axisLine={false} fontSize={12} tickFormatter={(v)=>`${v} MHz`}/>
                          <YAxis dataKey="p" tickLine={false} axisLine={false} fontSize={12}/>
                          <RTooltip cursor={false} />
                          <Area type="monotone" dataKey="p" stroke="currentColor" fillOpacity={0.15} fill="currentColor" strokeWidth={2} />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Label>Frequenz (MHz)</Label>
                    <Input defaultValue="868.100"/>
                    <Label>Bandbreite (kHz)</Label>
                    <Input defaultValue="125"/>
                    <Label>Modus</Label>
                    <Select defaultValue="rx">
                      <SelectTrigger><SelectValue/></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="rx">RX</SelectItem>
                        <SelectItem value="tx">TX</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button><Activity className="h-4 w-4 mr-2"/>Start</Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* ANTENNA */}
            <TabsContent value="antenna" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><Antenna className="h-4 w-4 mr-2"/>Antenna Automation</CardTitle>
                  <CardDescription>4-fach Diversity • GPIO-Steuerung</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-3 gap-4">
                  {[1,2,3,4].map(idx => (
                    <Card key={idx} className="border-dashed">
                      <CardHeader>
                        <CardTitle className="text-sm">Antenne {idx}</CardTitle>
                        <CardDescription>VSWR, Gain, Port</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <Metric label="VSWR" value={(1.4+idx*0.1).toFixed(2)} />
                        <Metric label="Gain" value={`${(2.5+idx*0.4).toFixed(1)} dBi`} />
                        <div className="flex items-center gap-2">
                          <Switch defaultChecked/>
                          <span className="text-xs">Aktiv</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>

            {/* APIs */}
            <TabsContent value="api" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><Globe2 className="h-4 w-4 mr-2"/>APIs & Integrationen</CardTitle>
                  <CardDescription>REST / WebSocket / GraphQL</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>REST</Label>
                    <Input readOnly value="http://localhost:8080/api/v1"/>
                    <Label>WebSocket</Label>
                    <Input readOnly value="ws://localhost:8080/ws/metrics"/>
                    <Label>GraphQL</Label>
                    <Input readOnly value="http://localhost:8080/graphql"/>
                  </div>
                  <div className="space-y-2">
                    <Label>Aktion</Label>
                    <div className="flex gap-2">
                      <Button size="sm"><Upload className="h-4 w-4 mr-2"/>POST /rf/tx</Button>
                      <Button size="sm" variant="outline"><Download className="h-4 w-4 mr-2"/>GET /rf/status</Button>
                    </div>
                    <Label>Universitäre APIs</Label>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <Chip>TU Dresden</Chip>
                      <Chip>MIT</Chip>
                      <Chip>Stanford</Chip>
                      <Chip>ETH Zürich</Chip>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Auth</Label>
                    <div className="flex items-center gap-2">
                      <Switch defaultChecked/> <span className="text-xs">Token</span>
                    </div>
                    <Input placeholder="Bearer …"/>
                    <Button variant="secondary"><ShieldCheck className="h-4 w-4 mr-2"/>Signierte Requests</Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* COMPLIANCE */}
            <TabsContent value="compliance" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><ShieldCheck className="h-4 w-4 mr-2"/>Compliance & Audit</CardTitle>
                  <CardDescription>Regulatorik, Whitelist, Audit-Chain</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-3">
                    <Label>Region/Regelwerk</Label>
                    <Select defaultValue="EU">
                      <SelectTrigger><SelectValue/></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="EU">EU (ETSI)</SelectItem>
                        <SelectItem value="US">US (FCC)</SelectItem>
                        <SelectItem value="Other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="space-y-2 text-xs">
                      <div className="flex items-center gap-2"><Checkbox id="c1" defaultChecked/><label htmlFor="c1">TX nur auf erlaubten Bändern</label></div>
                      <div className="flex items-center gap-2"><Checkbox id="c2" defaultChecked/><label htmlFor="c2">Leistungsbegrenzung aktiv</label></div>
                      <div className="flex items-center gap-2"><Checkbox id="c3" defaultChecked/><label htmlFor="c3">Automatische Band-Checks</label></div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Label>Audit-Kette</Label>
                    <div className="grid gap-2 text-xs">
                      <Input readOnly value="Chain: rf_hf_audit_chain"/>
                      <Input readOnly value="Status: verifiziert"/>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm"><Upload className="h-4 w-4 mr-2"/>Commit</Button>
                      <Button size="sm" variant="outline"><Download className="h-4 w-4 mr-2"/>Export JSON</Button>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Label>Risiko-Hinweise</Label>
                    <Alert>
                      <ShieldCheck className="h-4 w-4" />
                      <AlertTitle>Nur empfangen ist frei</AlertTitle>
                      <AlertDescription>Aktive Aussendungen können genehmigungspflichtig sein.</AlertDescription>
                    </Alert>
                    <Alert>
                      <Lock className="h-4 w-4" />
                      <AlertTitle>Hardware-Grenzen</AlertTitle>
                      <AlertDescription>Band-Freischaltung ist gerätespezifisch und nicht immer möglich.</AlertDescription>
                    </Alert>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* TOOLS */}
            <TabsContent value="tools" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center"><Wand2 className="h-4 w-4 mr-2"/>Werkzeuge</CardTitle>
                  <CardDescription>FW Overlay • GPIO • Exporte</CardDescription>
                </CardHeader>
                <CardContent className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Firmware Overlay</Label>
                    <div className="flex gap-2">
                      <Button size="sm"><Upload className="h-4 w-4 mr-2"/>Laden</Button>
                      <Button size="sm" variant="outline"><PauseCircle className="h-4 w-4 mr-2"/>Entfernen</Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>GPIO</Label>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      {["P1","P2","P3","P4","P5","P6"].map(p=> (
                        <Button key={p} size="sm" variant="outline">{p}</Button>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Backups</Label>
                    <div className="flex gap-2">
                      <Button size="sm"><Download className="h-4 w-4 mr-2"/>Config</Button>
                      <Button size="sm" variant="outline"><Upload className="h-4 w-4 mr-2"/>Import</Button>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="text-xs text-muted-foreground">
                  UI-Demo: Buttons rufen Platzhalter-Funktionen auf. Backend-Endpunkte können unter „APIs" konfiguriert werden.
                </CardFooter>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* footer */}
        <div className="max-w-7xl mx-auto px-4 py-8 text-center text-xs text-muted-foreground">
          <div className="flex items-center justify-center gap-2">
            <Cable className="h-3 w-3"/> <span>Designed for extensibility • v0 demo</span>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}
