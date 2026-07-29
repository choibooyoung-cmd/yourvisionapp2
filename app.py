<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP & Google Sheets 연동 자재 관리 시스템</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Pretendard Font -->
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css">
    <style>
        body { font-family: 'Pretendard', sans-serif; }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 antialiased h-screen flex overflow-hidden">

    <!-- Sidebar Navigation -->
    <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col justify-between border-r border-slate-800 shadow-xl z-20">
        <div>
            <!-- Logo & Brand -->
            <div class="p-5 border-b border-slate-800 flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg">
                    <i class="fa-solid fa-boxes-stacked text-lg"></i>
                </div>
                <div>
                    <h1 class="font-bold text-white text-sm tracking-tight">SCM & ERP Hub</h1>
                    <p class="text-[11px] text-slate-400">Google Sheets Connected</p>
                </div>
            </div>

            <!-- Navigation Menu -->
            <nav class="p-4 space-y-1.5">
                <button onclick="switchTab('dashboard')" id="nav-dashboard" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all bg-blue-600 text-white shadow-md">
                    <i class="fa-solid fa-chart-pie w-5"></i>
                    <span>종합 대시보드</span>
                </button>
                <button onclick="switchTab('inbound')" id="nav-inbound" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-truck-ramp-box w-5"></i>
                    <span>자재 입고 (MIGO)</span>
                </button>
                <button onclick="switchTab('outbound')" id="nav-outbound" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-dolly w-5"></i>
                    <span>자재 출고 (GI)</span>
                </button>
                <button onclick="switchTab('inventory')" id="nav-inventory" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-warehouse w-5"></i>
                    <span>실시간 재고 현황</span>
                </button>
                <button onclick="switchTab('sheets')" id="nav-sheets" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-file-excel w-5 text-emerald-400"></i>
                    <span>구글 스프레드시트 연동</span>
                </button>
                <button onclick="switchTab('logs')" id="nav-logs" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-terminal w-5"></i>
                    <span>인터페이스 연동 로그</span>
                </button>
            </nav>
        </div>

        <!-- Sidebar Footer Status -->
        <div class="p-4 border-t border-slate-800 bg-slate-950/50">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>Sheets API 연동</span>
                <span id="sheetSyncStatusBadge" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">대기 중</span>
            </div>
            <div class="flex items-center justify-between text-xs text-slate-400">
                <span>미전송 트랜잭션</span>
                <span id="pendingTxCount" class="font-mono font-bold text-amber-400">0 건</span>
            </div>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col h-screen overflow-hidden bg-slate-100">
        <!-- Top Header -->
        <header class="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between z-10 shadow-xs">
            <div>
                <h2 id="pageTitle" class="text-base font-bold text-slate-800">ERP 및 스프레드시트 연동 자재 관리 종합 대시보드</h2>
                <p id="pageDescription" class="text-xs text-slate-500">실시간 자재 수급 상태 및 Google Sheets / SAP ERP 동기화 트랜잭션을 관리합니다.</p>
            </div>
            <div class="flex items-center gap-3">
                <button onclick="openInboundModal()" class="px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-2">
                    <i class="fa-solid fa-plus"></i> 입고 등록
                </button>
                <button onclick="openOutboundModal()" class="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-2">
                    <i class="fa-solid fa-minus"></i> 출고 승인
                </button>
                <div class="h-6 w-px bg-slate-200"></div>
                <button onclick="triggerErpSync()" class="px-3 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-2">
                    <i id="syncIcon" class="fa-solid fa-rotate"></i> ERP & Sheets 동기화
                </button>
            </div>
        </header>

        <!-- Scrollable Body Content -->
        <div class="flex-1 overflow-y-auto p-6">

            <!-- 1. DASHBOARD TAB -->
            <div id="tab-content-dashboard" class="space-y-6">
                <!-- KPI Metrics Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
                        <div>
                            <p class="text-xs font-medium text-slate-500">전체 관리 자재 품목</p>
                            <h3 id="kpi-total-items" class="text-2xl font-bold text-slate-800 mt-1">0 품목</h3>
                            <span class="text-[11px] text-emerald-600 font-medium mt-1 inline-block"><i class="fa-solid fa-arrow-up"></i> 정상 마스터 연동</span>
                        </div>
                        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xl">
                            <i class="fa-solid fa-boxes-packing"></i>
                        </div>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
                        <div>
                            <p class="text-xs font-medium text-slate-500">금일 입고 건수</p>
                            <h3 id="kpi-inbound-today" class="text-2xl font-bold text-slate-800 mt-1">0 건</h3>
                            <span id="kpi-inbound-amount" class="text-[11px] text-slate-500 mt-1 inline-block">누적 수량: 0 EA</span>
                        </div>
                        <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl">
                            <i class="fa-solid fa-truck-fast"></i>
                        </div>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
                        <div>
                            <p class="text-xs font-medium text-slate-500">금일 출고 건수</p>
                            <h3 id="kpi-outbound-today" class="text-2xl font-bold text-slate-800 mt-1">0 건</h3>
                            <span id="kpi-outbound-amount" class="text-[11px] text-slate-500 mt-1 inline-block">누적 수량: 0 EA</span>
                        </div>
                        <div class="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-xl">
                            <i class="fa-solid fa-dolly"></i>
                        </div>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
                        <div>
                            <p class="text-xs font-medium text-slate-500">안전재고 미달 (경고)</p>
                            <h3 id="kpi-low-stock" class="text-2xl font-bold text-rose-600 mt-1">0 품목</h3>
                            <span class="text-[11px] text-rose-500 font-medium mt-1 inline-block"><i class="fa-solid fa-triangle-exclamation"></i> 즉시 발주 필요</span>
                        </div>
                        <div class="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center text-xl">
                            <i class="fa-solid fa-circle-exclamation"></i>
                        </div>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs lg:col-span-2">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-bold text-slate-800 text-sm">최근 7일 간 자재 수급 트렌드 (입고 vs 출고)</h3>
                            <span class="text-xs text-slate-400 font-mono">Real-time Analytics</span>
                        </div>
                        <div class="h-64">
                            <canvas id="trendChart"></canvas>
                        </div>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-bold text-slate-800 text-sm">카테고리별 자재 자산 비중</h3>
                            <span class="text-xs text-slate-400 font-mono">Valuation</span>
                        </div>
                        <div class="h-64 flex items-center justify-center">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Low Stock Quick Action Table & Logs Stream -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="font-bold text-slate-800 text-sm">안전재고 미달 품목 즉시 발주 리스트</h3>
                            <button onclick="simulateErpAutoOrder()" class="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-2.5 py-1 rounded-lg font-semibold">전체 자동 발주 (PR)</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead>
                                    <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                        <th class="p-2.5">코드</th>
                                        <th class="p-2.5">품목명</th>
                                        <th class="p-2.5 text-right">현재고</th>
                                        <th class="p-2.5 text-right">안전재고</th>
                                        <th class="p-2.5 text-center">액션</th>
                                    </tr>
                                </thead>
                                <tbody id="dashboardLowStockBody" class="divide-y divide-slate-100">
                                    <!-- Dynamic Rendered -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-3">
                                <h3 class="font-bold text-slate-800 text-sm">실시간 인터페이스 및 시트 연동 로그</h3>
                                <span class="text-xs text-emerald-600 font-medium">● Connected</span>
                            </div>
                            <div id="dashboardLogsStream" class="space-y-2 font-mono text-xs">
                                <!-- Dynamic Rendered Logs -->
                            </div>
                        </div>
                        <div class="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                            <span>Google Sheets 웹훅 연동 상태: <strong class="text-emerald-600">정상 통신 중</strong></span>
                            <button onclick="switchTab('sheets')" class="text-blue-600 hover:underline font-semibold">시트 연동 설정 가기 &rarr;</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. INBOUND TAB -->
            <div id="tab-content-inbound" class="hidden space-y-4">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
                    <div class="flex items-center gap-3 w-1/3">
                        <input type="text" id="inboundSearch" onkeyup="filterInboundTable()" placeholder="입고 번호, 자재명 또는 공급사 검색..." class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-blue-500">
                    </div>
                    <button onclick="openInboundModal()" class="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-semibold shadow-xs">신규 자재 입고 등록</button>
                </div>
                <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200">
                            <tr>
                                <th class="p-3">입고 번호 (MIGO)</th>
                                <th class="p-3">입고 일시</th>
                                <th class="p-3">자재 코드 / 명</th>
                                <th class="p-3 text-right">입고 수량</th>
                                <th class="p-3">공급사</th>
                                <th class="p-3">입고 위치</th>
                                <th class="p-3 text-center">ERP / Sheets 연동</th>
                            </tr>
                        </thead>
                        <tbody id="inboundTableBody" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <!-- 3. OUTBOUND TAB -->
            <div id="tab-content-outbound" class="hidden space-y-4">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
                    <div class="flex items-center gap-3 w-1/3">
                        <input type="text" id="outboundSearch" onkeyup="filterOutboundTable()" placeholder="출고번호, 자재명, 요청부서 검색..." class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-blue-500">
                    </div>
                    <button onclick="openOutboundModal()" class="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold shadow-xs">자재 불출 승인</button>
                </div>
                <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200">
                            <tr>
                                <th class="p-3">출고 번호 (GI)</th>
                                <th class="p-3">출고 일시</th>
                                <th class="p-3">자재 코드 / 명</th>
                                <th class="p-3 text-right">출고 수량</th>
                                <th class="p-3">청구 부서</th>
                                <th class="p-3">요청자</th>
                                <th class="p-3 text-center">원가회계(CO) 및 연동</th>
                            </tr>
                        </thead>
                        <tbody id="outboundTableBody" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <!-- 4. INVENTORY TAB -->
            <div id="tab-content-inventory" class="hidden space-y-4">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between flex-wrap gap-3">
                    <div class="flex items-center gap-3">
                        <select id="categoryFilter" onchange="renderInventoryTable()" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700">
                            <option value="ALL">전체 카테고리</option>
                            <option value="원자재">원자재</option>
                            <option value="부자재">부자재</option>
                            <option value="전자부품">전자부품</option>
                            <option value="포장재">포장재</option>
                        </select>
                        <select id="stockStatusFilter" onchange="renderInventoryTable()" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700">
                            <option value="ALL">재고 상태 전체</option>
                            <option value="LOW">안전재고 미달 (LOW)</option>
                            <option value="NORMAL">정상 (NORMAL)</option>
                        </select>
                    </div>
                    <div class="flex items-center gap-3">
                        <input type="text" id="inventorySearch" onkeyup="renderInventoryTable()" placeholder="품목명 또는 코드 검색..." class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-blue-500 w-64">
                        <button onclick="exportInventoryToSheet()" class="px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold flex items-center gap-2 shadow-xs">
                            <i class="fa-solid fa-file-excel"></i> 구글 시트로 재고 동기화
                        </button>
                    </div>
                </div>
                <div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 text-slate-500 border-b border-slate-200">
                            <tr>
                                <th class="p-3">자재 코드</th>
                                <th class="p-3">품목명</th>
                                <th class="p-3">카테고리</th>
                                <th class="p-3 text-right">현재고</th>
                                <th class="p-3 text-right">안전재고</th>
                                <th class="p-3 text-right">단가</th>
                                <th class="p-3 text-right">재고 총액</th>
                                <th class="p-3">창고 위치 (Bin)</th>
                                <th class="p-3 text-center">상태</th>
                                <th class="p-3 text-center">발주</th>
                            </tr>
                        </thead>
                        <tbody id="inventoryTableBody" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <!-- 5. GOOGLE SHEETS SETTINGS & INTEGRATION TAB (NEW) -->
            <div id="tab-content-sheets" class="hidden space-y-6">
                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
                    <div class="flex items-center gap-3 pb-4 border-b border-slate-100">
                        <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl">
                            <i class="fa-solid fa-file-excel"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-800 text-sm">구글 스프레드시트(Google Sheets) 연동 설정 센터</h3>
                            <p class="text-xs text-slate-500">Google Apps Script Web App URL을 연동하여 시스템의 입/출고 및 재고 데이터를 구글 스프레드시트와 실시간 송수신합니다.</p>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                        <div class="space-y-4">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">Google Apps Script 웹 앱(Web App) URL</label>
                                <input type="text" id="scriptWebHookUrl" placeholder="https://script.google.com/macros/s/..." class="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:border-blue-500">
                                <p class="text-[11px] text-slate-400 mt-1">구글 시트의 [확장 프로그램] &gt; [Apps Script]에서 배포된 웹 앱 URL을 입력하세요.</p>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">연동 대상 스프레드시트 문서 ID 또는 링크</label>
                                <input type="text" id="sheetTargetId" placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" class="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:border-blue-500">
                            </div>
                            <div class="flex gap-2 pt-2">
                                <button onclick="saveSheetConfig()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-sm">설정 저장 및 연결 테스트</button>
                                <button onclick="fetchDataFromGoogleSheet()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm flex items-center gap-2">
                                    <i class="fa-solid fa-cloud-arrow-down"></i> 시트에서 데이터 가져오기
                                </button>
                            </div>
                        </div>

                        <div class="bg-slate-900 text-slate-200 p-5 rounded-2xl font-mono text-[11px] space-y-3 flex flex-col justify-between">
                            <div>
                                <div class="text-slate-400 font-bold mb-2 flex items-center gap-2">
                                    <i class="fa-solid fa-code text-emerald-400"></i> Google Apps Script 연동 스크립트 가이드 (참고용)
                                </div>
                                <pre class="text-slate-300 overflow-x-auto text-[10px] bg-slate-950 p-3 rounded-xl border border-slate-800">
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  
  if(data.type === "INBOUND") {
    sheet.appendRow([data.id, data.date, data.code, data.name, data.qty, data.vendor]);
  } else if(data.type === "INVENTORY_SYNC") {
    // 재고 마스터 일괄 업데이트 로직
  }
  return ContentService.createTextOutput(JSON.stringify({"status":"success"}))
         .setMimeType(ContentService.MimeType.JSON);
}</pre>
                            </div>
                            <div class="text-[11px] text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800">
                                <span>현재 연동 모드: <span id="syncModeIndicator" class="text-emerald-400 font-bold">비동기 웹훅 (JSON)</span></span>
                                <span id="lastSheetSyncTime" class="text-slate-500">동기화 이력 없음</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 6. INTERFACE LOGS TAB -->
            <div id="tab-content-logs" class="hidden space-y-4">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
                    <h3 class="font-bold text-slate-800 text-sm">ERP / WMS / Google Sheets 인터페이스 트랜잭션 로그</h3>
                    <button onclick="clearLogs()" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold">로그 초기화</button>
                </div>
                <div class="bg-slate-950 text-slate-200 p-5 rounded-2xl font-mono text-xs shadow-inner space-y-3 min-h-[400px]" id="fullLogContainer">
                    <!-- Dynamic Rendered -->
                </div>
            </div>

        </div>
    </main>

    <!-- Modal: Inbound Registration -->
    <div id="inboundModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs hidden items-center justify-center z-50">
        <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
                <h3 class="font-bold text-slate-800 text-sm flex items-center gap-2">
                    <i class="fa-solid fa-truck-ramp-box text-emerald-600"></i> 자재 입고 등록 (SAP MIGO 연동)
                </h3>
                <button onclick="closeInboundModal()" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form id="inboundForm" onsubmit="handleInboundSubmit(event)" class="p-5 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">입고 자재 선택</label>
                    <select id="inboundMaterialCode" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:border-blue-500"></select>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">입고 수량 (EA)</label>
                        <input type="number" id="inboundQty" min="1" value="100" required class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">입고 위치 (Bin)</label>
                        <input type="text" id="inboundLocation" value="A1-Zone-01" required class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:border-blue-500">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">공급사 명</label>
                    <input type="text" id="inboundVendor" value="(주)한국소재산업" required class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-blue-500">
                </div>
                <div class="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-[11px] text-emerald-800 flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-emerald-600"></i>
                    <span>입고 등록 시 구글 스프레드시트 및 ERP 재고 장부에 실시간 자동 반영됩니다.</span>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeInboundModal()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">취소</button>
                    <button type="submit" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-md transition-all">입고 승인 및 시트 연동</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: Outbound Registration -->
    <div id="outboundModal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs hidden items-center justify-center z-50">
        <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
                <h3 class="font-bold text-slate-800 text-sm flex items-center gap-2">
                    <i class="fa-solid fa-dolly text-indigo-600"></i> 자재 출고 승인 (ERP CO 연동)
                </h3>
                <button onclick="closeOutboundModal()" class="text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form id="outboundForm" onsubmit="handleOutboundSubmit(event)" class="p-5 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">출고 자재 선택</label>
                    <select id="outboundMaterialCode" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:border-blue-500"></select>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">출고 수량 (EA)</label>
                        <input type="number" id="outboundQty" min="1" value="50" required class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">청구 부서</label>
                        <input type="text" id="outboundDept" value="조립 1라인 / 생산팀" required class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-blue-500">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">요청자 성명</label>
                    <input type="text" id="outboundRequester" value="김조립 대리" required class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-blue-500">
                </div>
                <div class="p-3 bg-indigo-50 rounded-lg border border-indigo-100 text-[11px] text-indigo-800 flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-indigo-600"></i>
                    <span>출고 승인 시 스프레드시트 출고 로그 시트 및 ERP CO(원가통제) 모듈과 연동됩니다.</span>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeOutboundModal()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">취소</button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-md transition-all">출고 승인 및 ERP 연동</button>
                </div>
            </form>
        </div>
    </div>

    <!-- JavaScript Application Logic with Google Sheets Integration -->
    <script>
        // --- Mock Data Store ---
        let materialsData = [
            { code: "MAT-1001", name: "고장력 알루미늄 판재", category: "원자재", stock: 1450, safety: 500, price: 18500, location: "A1-Zone-01", status: "NORMAL" },
            { code: "MAT-1002", name: "SUS304 스테인리스 코일", category: "원자재", stock: 320, safety: 400, price: 32000, location: "A1-Zone-02", status: "LOW" },
            { code: "PAR-2001", name: "정밀 육각 볼트 (M8x30)", category: "부자재", stock: 12500, safety: 5000, price: 120, location: "B2-Rack-11", status: "NORMAL" },
            { code: "PAR-2002", name: "산업용 실링 가스켓", category: "부자재", stock: 180, safety: 300, price: 2400, location: "B2-Rack-15", status: "LOW" },
            { code: "ELE-3001", name: "PLC 메인 제어 마이크로칩", category: "전자부품", stock: 85, safety: 100, price: 145000, location: "C3-Safe-01", status: "LOW" },
            { code: "ELE-3002", name: "서보 모터 드라이버 (AC 220V)", category: "전자부품", stock: 210, safety: 80, price: 280000, location: "C3-Rack-04", status: "NORMAL" },
            { code: "PAC-4001", name: "고강도 수출용 파렛트", category: "포장재", stock: 450, safety: 150, price: 15000, location: "D1-Yard-01", status: "NORMAL" },
            { code: "PAC-4002", name: "완충 에어캡 보호 패드", category: "포장재", stock: 95, safety: 200, price: 3500, location: "D1-Rack-08", status: "LOW" }
        ];

        let inboundHistory = [
            { id: "IN-2026-0729-01", date: "2026-07-29 09:15", code: "MAT-1001", name: "고장력 알루미늄 판재", qty: 500, vendor: "(주)한국소재산업", location: "A1-Zone-01", erpStatus: "SYNCED" },
            { id: "IN-2026-0728-02", date: "2026-07-28 14:30", code: "PAR-2001", name: "정밀 육각 볼트 (M8x30)", qty: 3000, vendor: "대성테크", location: "B2-Rack-11", erpStatus: "SYNCED" }
        ];

        let outboundHistory = [
            { id: "OUT-2026-0729-01", date: "2026-07-29 11:20", code: "ELE-3002", name: "서보 모터 드라이버 (AC 220V)", qty: 20, dept: "조립 1라인 / 생산팀", requester: "김조립 대리", erpStatus: "SETTLED" },
            { id: "OUT-2026-0728-01", date: "2026-07-28 16:45", code: "MAT-1001", name: "고장력 알루미늄 판재", qty: 150, dept: "프레스 공정 / 제조부", requester: "이프레스 과장", erpStatus: "SETTLED" }
        ];

        let logs = [
            { time: "16:35:10", type: "INFO", module: "SHEETS-API", message: "Google Sheets Web App endpoint initialized. Ready for bidirectional sync." },
            { time: "16:20:05", type: "SUCCESS", module: "SAP-MIGO", message: "Inbound doc [IN-2026-0729-01] posted to SAP MM inventory ledger & Sheet." },
            { time: "14:11:50", type: "WARNING", module: "WMS-ALERT", message: "Low stock threshold triggered for [ELE-3001] PLC 메인 제어 마이크로칩 (Stock: 85 < Safety: 100)." },
            { time: "11:20:00", type: "SUCCESS", module: "SAP-CO", message: "Outbound document [OUT-2026-0729-01] cost center allocation processed." }
        ];

        let pendingTxCount = 0;
        let trendChartInstance = null;
        let categoryChartInstance = null;
        let sheetConfig = {
            url: "",
            targetId: ""
        };

        // --- Initialization on Load ---
        document.addEventListener("DOMContentLoaded", () => {
            initCharts();
            renderDashboard();
            renderInboundTable();
            renderOutboundTable();
            renderInventoryTable();
            renderLogs();
            populateMaterialSelects();
        });

        // --- Tab Navigation Switcher ---
        function switchTab(tabName) {
            const tabs = ['dashboard', 'inbound', 'outbound', 'inventory', 'sheets', 'logs'];
            tabs.forEach(t => {
                const content = document.getElementById(`tab-content-${t}`);
                const btn = document.getElementById(`nav-${t}`);
                if (t === tabName) {
                    content.classList.remove('hidden');
                    btn.className = "nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all bg-blue-600 text-white shadow-md";
                } else {
                    content.classList.add('hidden');
                    btn.className = "nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400";
                }
            });

            // Update Header Titles
            const titles = {
                dashboard: { title: "ERP 및 스프레드시트 연동 자재 관리 종합 대시보드", desc: "실시간 자재 수급 상태 및 Google Sheets / SAP ERP 동기화 트랜잭션을 관리합니다." },
                inbound: { title: "자재 입고 관리 (Inbound MIGO)", desc: "외부 공급사로부터 입고되는 자재를 검수하고 SAP 재고 장부 및 구글 시트에 즉시 반영합니다." },
                outbound: { title: "자재 출고 관리 (Outbound Goods Issue)", desc: "생산 현장 불출 요청 승인 및 원가 회계 계정 연동 현황을 관리합니다." },
                inventory: { title: "실시간 자재 재고 현황 (Real-time SCM Inventory)", desc: "창고 위치별 실물 재고와 구글 스프레드시트 간의 실시간 비교 및 동기화." },
                sheets: { title: "구글 스프레드시트(Google Sheets) 연동 센터", desc: "웹 앱훅을 통한 스프레드시트 양방향 데이터 연동 및 자동 내보내기 설정." },
                logs: { title: "ERP 인터페이스 연동 로그 (API / SAP / Sheets)", desc: "자재 시스템과 외부 ERP 및 구글 스프레드시트 간 실시간 통신 히스토리 및 장애 추적 로그." }
            };
            document.getElementById("pageTitle").innerText = titles[tabName].title;
            document.getElementById("pageDescription").innerText = titles[tabName].desc;
        }

        // --- Google Sheets Integration Functions ---
        function saveSheetConfig() {
            const urlInput = document.getElementById("scriptWebHookUrl").value.trim();
            const targetIdInput = document.getElementById("sheetTargetId").value.trim();

            if (!urlInput) {
                alert("Google Apps Script 웹 앱 URL을 올바르게 입력해주세요.");
                return;
            }

            sheetConfig.url = urlInput;
            sheetConfig.targetId = targetIdInput;

            document.getElementById("sheetSyncStatusBadge").className = "px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
            document.getElementById("sheetSyncStatusBadge").innerText = "연동됨";

            const now = new Date();
            const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
            document.getElementById("lastSheetSyncTime").innerText = timeStr + " 연결됨";

            logs.unshift({
                time: timeStr,
                type: "SUCCESS",
                module: "SHEETS-API",
                message: `Google Sheets Web App connection configured successfully. Target ID: ${targetIdInput || 'Default'}`
            });
            renderLogs();
            showToast("구글 스프레드시트 연동 설정이 성공적으로 저장되었습니다!");
        }

        // Send transaction data to Google Sheets via Fetch Webhook
        async function sendDataToGoogleSheet(payloadType, payloadData) {
            if (!sheetConfig.url) {
                // 웹훅 URL이 설정되지 않은 경우 시뮬레이션 로깅만 수행
                console.warn("[Sheets Mock] Webhook URL not configured. Data saved locally.");
                return;
            }

            try {
                const response = await fetch(sheetConfig.url, {
                    method: 'POST',
                    mode: 'no-cors', // CORS 우회용
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: payloadType, ...payloadData })
                });

                const now = new Date();
                const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
                
                logs.unshift({
                    time: timeStr,
                    type: "SUCCESS",
                    module: "SHEETS-SYNC",
                    message: `Successfully synchronized [${payloadType}] transaction to Google Sheets.`
                });
                renderLogs();
            } catch (err) {
                console.error("Google Sheets sync error:", err);
                logs.unshift({
                    time: new Date().toLocaleTimeString(),
                    type: "WARNING",
                    module: "SHEETS-ERROR",
                    message: `Failed to push [${payloadType}] to Google Sheets. Check Web App URL.`
                });
                renderLogs();
            }
        }

        function exportInventoryToSheet() {
            showToast("현재 재고 마스터 데이터를 구글 스프레드시트로 내보내는 중...");
            sendDataToGoogleSheet("INVENTORY_SYNC", { items: materialsData });
            
            setTimeout(() => {
                showToast("구글 스프레드시트 재고 시트에 최신 재고가 동기화되었습니다!");
            }, 1000);
        }

        async function fetchDataFromGoogleSheet() {
            if (!sheetConfig.url) {
                alert("먼저 구글 Apps Script 웹 앱 URL을 설정하고 저장해주세요.");
                switchTab('sheets');
                return;
            }

            showToast("구글 스프레드시트에서 최신 데이터를 불러오는 중...");
            
            // 시뮬레이션 연동 성공 처리
            setTimeout(() => {
                const now = new Date();
                logs.unshift({
                    time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                    type: "SUCCESS",
                    module: "SHEETS-IMPORT",
                    message: "Successfully fetched updated inventory list from Google Sheets."
                });
                renderLogs();
                showToast("구글 스프레드시트와의 데이터 동기화 및 갱신이 완료되었습니다.");
            }, 1200);
        }

        // --- Render Dashboard Metrics & Tables ---
        function renderDashboard() {
            const totalItems = materialsData.length;
            const lowStockCount = materialsData.filter(m => m.stock < m.safety).length;
            const todayInboundCount = inboundHistory.length;
            const todayInboundQty = inboundHistory.reduce((acc, cur) => acc + cur.qty, 0);
            const todayOutboundCount = outboundHistory.length;
            const todayOutboundQty = outboundHistory.reduce((acc, cur) => acc + cur.qty, 0);

            document.getElementById("kpi-total-items").innerText = totalItems + " 품목";
            document.getElementById("kpi-inbound-today").innerText = todayInboundCount + " 건";
            document.getElementById("kpi-inbound-amount").innerText = `누적 수량: ${todayInboundQty.toLocaleString()} EA`;
            document.getElementById("kpi-outbound-today").innerText = todayOutboundCount + " 건";
            document.getElementById("kpi-outbound-amount").innerText = `누적 수량: ${todayOutboundQty.toLocaleString()} EA`;
            document.getElementById("kpi-low-stock").innerText = lowStockCount + " 품목";

            // Low Stock Table in Dashboard
            const lowStockItems = materialsData.filter(m => m.stock < m.safety);
            const tbody = document.getElementById("dashboardLowStockBody");
            tbody.innerHTML = "";
            if (lowStockItems.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400">현재 안전재고 미달 품목이 없습니다.</td></tr>`;
            } else {
                lowStockItems.forEach(item => {
                    tbody.innerHTML += `
                        <tr class="hover:bg-slate-50/80 transition-colors">
                            <td class="p-2.5 font-mono font-medium text-slate-700">${item.code}</td>
                            <td class="p-2.5 font-semibold text-slate-900">${item.name}</td>
                            <td class="p-2.5 text-right font-bold text-rose-600">${item.stock.toLocaleString()} EA</td>
                            <td class="p-2.5 text-right text-slate-500">${item.safety.toLocaleString()} EA</td>
                            <td class="p-2.5 text-center">
                                <button onclick="triggerAutoOrderFor('${item.code}')" class="px-2 py-1 bg-amber-500 hover:bg-amber-600 text-white rounded text-[10px] font-semibold shadow-xs">자동발주</button>
                            </td>
                        </tr>
                    `;
                });
            }

            // Dashboard Logs Stream Snippet
            const streamContainer = document.getElementById("dashboardLogsStream");
            streamContainer.innerHTML = "";
            logs.slice(0, 5).forEach(log => {
                const badgeColor = log.type === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : log.type === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20';
                streamContainer.innerHTML += `
                    <div class="p-2 bg-slate-900 rounded-lg border border-slate-800 text-[11px] font-mono flex items-center justify-between">
                        <div class="flex items-center gap-2 overflow-hidden">
                            <span class="px-1.5 py-0.5 rounded text-[9px] font-bold border ${badgeColor}">${log.module}</span>
                            <span class="text-slate-300 truncate">${log.message}</span>
                        </div>
                        <span class="text-slate-500 text-[10px] flex-shrink-0 ml-2">${log.time}</span>
                    </div>
                `;
            });
        }

        // --- Render Tables for Sub-tabs ---
        function renderInboundTable() {
            const searchVal = document.getElementById("inboundSearch").value.toLowerCase();
            const tbody = document.getElementById("inboundTableBody");
            tbody.innerHTML = "";
            const filtered = inboundHistory.filter(i => i.name.toLowerCase().includes(searchVal) || i.code.toLowerCase().includes(searchVal) || i.vendor.toLowerCase().includes(searchVal));

            if(filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-400">입고 내역이 없습니다.</td></tr>`;
                return;
            }

            filtered.forEach(item => {
                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-mono font-bold text-slate-700">${item.id}</td>
                        <td class="p-3 text-slate-500 text-xs">${item.date}</td>
                        <td class="p-3"><span class="font-mono text-xs text-blue-600 font-semibold">${item.code}</span><br><span class="font-medium text-slate-800">${item.name}</span></td>
                        <td class="p-3 text-right font-bold text-emerald-600">+${item.qty.toLocaleString()} EA</td>
                        <td class="p-3 text-slate-700">${item.vendor}</td>
                        <td class="p-3"><span class="px-2 py-0.5 bg-slate-100 rounded text-[11px] font-mono text-slate-600">${item.location}</span></td>
                        <td class="p-3 text-center">
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                                <i class="fa-solid fa-check mr-1"></i> SAP & 시트 연동완료
                            </span>
                        </td>
                    </tr>
                `;
            });
        }

        function filterInboundTable() { renderInboundTable(); }

        function renderOutboundTable() {
            const searchVal = document.getElementById("outboundSearch").value.toLowerCase();
            const tbody = document.getElementById("outboundTableBody");
            tbody.innerHTML = "";
            const filtered = outboundHistory.filter(o => o.name.toLowerCase().includes(searchVal) || o.code.toLowerCase().includes(searchVal) || o.dept.toLowerCase().includes(searchVal) || o.requester.toLowerCase().includes(searchVal));

            if(filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-400">출고 내역이 없습니다.</td></tr>`;
                return;
            }

            filtered.forEach(item => {
                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-mono font-bold text-slate-700">${item.id}</td>
                        <td class="p-3 text-slate-500 text-xs">${item.date}</td>
                        <td class="p-3"><span class="font-mono text-xs text-indigo-600 font-semibold">${item.code}</span><br><span class="font-medium text-slate-800">${item.name}</span></td>
                        <td class="p-3 text-right font-bold text-indigo-600">-${item.qty.toLocaleString()} EA</td>
                        <td class="p-3 text-slate-700 font-medium">${item.dept}</td>
                        <td class="p-3 text-slate-600">${item.requester}</td>
                        <td class="p-3 text-center">
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                                <i class="fa-solid fa-check mr-1"></i> CO 정산완료
                            </span>
                        </td>
                    </tr>
                `;
            });
        }

        function filterOutboundTable() { renderOutboundTable(); }

        function renderInventoryTable() {
            const catFilter = document.getElementById("categoryFilter").value;
            const statusFilter = document.getElementById("stockStatusFilter").value;
            const searchVal = document.getElementById("inventorySearch").value.toLowerCase();

            const tbody = document.getElementById("inventoryTableBody");
            tbody.innerHTML = "";

            let filtered = materialsData.filter(item => {
                const matchCat = catFilter === 'ALL' || item.category === catFilter;
                const matchStatus = statusFilter === 'ALL' || item.status === statusFilter;
                const matchSearch = item.name.toLowerCase().includes(searchVal) || item.code.toLowerCase().includes(searchVal);
                return matchCat && matchStatus && matchSearch;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="10" class="p-6 text-center text-slate-400">조건에 일치하는 자재가 없습니다.</td></tr>`;
                return;
            }

            filtered.forEach(item => {
                const totalVal = item.stock * item.price;
                const isLow = item.stock < item.safety;
                const statusBadge = isLow 
                    ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700 border border-rose-200">안전재고 미달</span>`
                    : `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">정상</span>`;

                tbody.innerHTML += `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-mono font-bold text-slate-700">${item.code}</td>
                        <td class="p-3 font-semibold text-slate-900">${item.name}</td>
                        <td class="p-3"><span class="px-2 py-0.5 bg-slate-100 rounded text-slate-600 text-[11px]">${item.category}</span></td>
                        <td class="p-3 text-right font-bold ${isLow ? 'text-rose-600' : 'text-slate-900'}">${item.stock.toLocaleString()} EA</td>
                        <td class="p-3 text-right text-slate-500">${item.safety.toLocaleString()} EA</td>
                        <td class="p-3 text-right text-slate-600 font-mono">${item.price.toLocaleString()} 원</td>
                        <td class="p-3 text-right font-bold text-slate-900 font-mono">${totalVal.toLocaleString()} 원</td>
                        <td class="p-3 font-mono text-xs text-slate-600">${item.location}</td>
                        <td class="p-3 text-center">${statusBadge}</td>
                        <td class="p-3 text-center">
                            <button onclick="triggerAutoOrderFor('${item.code}')" class="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-[10px] font-semibold shadow-xs">발주요청</button>
                        </td>
                    </tr>
                `;
            });
        }

        function renderLogs() {
            const container = document.getElementById("fullLogContainer");
            container.innerHTML = "";
            logs.forEach(log => {
                const color = log.type === 'SUCCESS' ? 'text-emerald-400' : log.type === 'WARNING' ? 'text-amber-400' : 'text-blue-400';
                container.innerHTML += `
                    <div class="flex items-start gap-3 pb-2 border-b border-slate-800/80">
                        <span class="text-slate-500">${log.time}</span>
                        <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 ${color}">${log.module}</span>
                        <span class="text-slate-200 flex-1">${log.message}</span>
                        <span class="text-slate-500 uppercase text-[10px]">${log.type}</span>
                    </div>
                `;
            });
        }

        function clearLogs() {
            logs = [];
            renderLogs();
            renderDashboard();
            showToast("연동 로그가 초기화되었습니다.");
        }

        // --- Modals Handlers ---
        function populateMaterialSelects() {
            const inboundSel = document.getElementById("inboundMaterialCode");
            const outboundSel = document.getElementById("outboundMaterialCode");
            inboundSel.innerHTML = "";
            outboundSel.innerHTML = "";

            materialsData.forEach(m => {
                const optHtml = `<option value="${m.code}">${m.code} - ${m.name} (현재고: ${m.stock} EA)</option>`;
                inboundSel.innerHTML += optHtml;
                outboundSel.innerHTML += optHtml;
            });
        }

        function openInboundModal() {
            document.getElementById("inboundModal").classList.remove("hidden");
            document.getElementById("inboundModal").classList.add("flex");
        }
        function closeInboundModal() {
            document.getElementById("inboundModal").classList.remove("flex");
            document.getElementById("inboundModal").classList.add("hidden");
        }

        function openOutboundModal() {
            document.getElementById("outboundModal").classList.remove("hidden");
            document.getElementById("outboundModal").classList.add("flex");
        }
        function closeOutboundModal() {
            document.getElementById("outboundModal").classList.remove("flex");
            document.getElementById("outboundModal").classList.add("hidden");
        }

        // --- Form Submissions with ERP & Sheets Simulation ---
        function handleInboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById("inboundMaterialCode").value;
            const qty = parseInt(document.getElementById("inboundQty").value);
            const vendor = document.getElementById("inboundVendor").value;
            const location = document.getElementById("inboundLocation").value || "A1-Zone-General";

            const targetMat = materialsData.find(m => m.code === code);
            if (!targetMat) return;

            targetMat.stock += qty;
            if (targetMat.stock >= targetMat.safety) targetMat.status = "NORMAL";

            const now = new Date();
            const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
            const newId = `IN-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${Math.floor(10 + Math.random()*90)}`;

            const newInboundRecord = {
                id: newId,
                date: timeStr,
                code: targetMat.code,
                name: targetMat.name,
                qty: qty,
                vendor: vendor,
                location: location,
                erpStatus: "SYNCED"
            };

            inboundHistory.unshift(newInboundRecord);

            // Send to Google Sheets via Webhook
            sendDataToGoogleSheet("INBOUND", newInboundRecord);

            logs.unshift({
                time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                type: "SUCCESS",
                module: "SAP-MIGO",
                message: `Inbound document [${newId}] successfully posted. Material [${targetMat.code}] stock increased by ${qty} EA.`
            });

            pendingTxCount++;
            document.getElementById("pendingTxCount").innerText = pendingTxCount + " 건";

            closeInboundModal();
            document.getElementById("inboundForm").reset();

            renderDashboard();
            renderInboundTable();
            renderInventoryTable();
            renderLogs();
            updateCharts();

            showToast(`신규 입고가 등록되고 구글 시트 및 ERP 장부에 반영되었습니다! (${targetMat.name} +${qty}EA)`);
        }

        function handleOutboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById("outboundMaterialCode").value;
            const qty = parseInt(document.getElementById("outboundQty").value);
            const dept = document.getElementById("outboundDept").value;
            const requester = document.getElementById("outboundRequester").value;

            const targetMat = materialsData.find(m => m.code === code);
            if (!targetMat) return;

            if (targetMat.stock < qty) {
                alert(`[재고 부족 오류] 출고 요청 수량(${qty} EA)이 현재고(${targetMat.stock} EA)를 초과합니다.`);
                return;
            }

            targetMat.stock -= qty;
            if (targetMat.stock < targetMat.safety) targetMat.status = "LOW";

            const now = new Date();
            const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
            const newId = `OUT-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${Math.floor(10 + Math.random()*90)}`;

            const newOutboundRecord = {
                id: newId,
                date: timeStr,
                code: targetMat.code,
                name: targetMat.name,
                qty: qty,
                dept: dept,
                requester: requester,
                erpStatus: "SETTLED"
            };

            outboundHistory.unshift(newOutboundRecord);

            // Send to Google Sheets via Webhook
            sendDataToGoogleSheet("OUTBOUND", newOutboundRecord);

            logs.unshift({
                time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                type: "SUCCESS",
                module: "SAP-CO",
                message: `Outbound goods issue [${newId}] processed. Material [${targetMat.code}] -${qty} EA allocated to [${dept}].`
            });

            pendingTxCount++;
            document.getElementById("pendingTxCount").innerText = pendingTxCount + " 건";

            closeOutboundModal();
            document.getElementById("outboundForm").reset();

            renderDashboard();
            renderOutboundTable();
            renderInventoryTable();
            renderLogs();
            updateCharts();

            showToast(`자재 출고 승인 및 구글 시트 원가 정산이 완료되었습니다! (${targetMat.name} -${qty}EA)`);
        }

        function triggerAutoOrderFor(code) {
            const item = materialsData.find(m => m.code === code);
            if (!item) return;
            const orderQty = (item.safety - item.stock) + 200;

            const now = new Date();
            logs.unshift({
                time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                type: "SUCCESS",
                module: "SAP-PURCHASE",
                message: `Automated Purchase Requisition (PR) created for [${item.code}] ${item.name}. Quantity: ${orderQty} EA.`
            });

            pendingTxCount++;
            document.getElementById("pendingTxCount").innerText = pendingTxCount + " 건";
            renderLogs();
            renderDashboard();

            showToast(`[${item.name}] 품목에 대한 ERP 자동 구매 발주서(PR)가 생성되었습니다! (+${orderQty} EA)`);
        }

        function simulateErpAutoOrder() {
            const lowItems = materialsData.filter(m => m.stock < m.safety);
            if (lowItems.length === 0) {
                showToast("현재 안전재고 미달 품목이 없어 발주할 대상이 없습니다.");
                return;
            }
            lowItems.forEach(item => triggerAutoOrderFor(item.code));
        }

        function triggerErpSync() {
            const syncIcon = document.getElementById("syncIcon");
            syncIcon.classList.add("fa-spin");
            
            setTimeout(() => {
                syncIcon.classList.remove("fa-spin");
                pendingTxCount = 0;
                document.getElementById("pendingTxCount").innerText = "0 건";
                
                const now = new Date();
                logs.unshift({
                    time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                    type: "SUCCESS",
                    module: "SAP-SHEETS-SYNC",
                    message: "Manual full-sync executed between SAP ERP, WMS, and Google Sheets."
                });
                renderLogs();
                renderDashboard();
                showToast("SAP ERP 및 구글 스프레드시트와의 실시간 동기화가 성공적으로 완료되었습니다!");
            }, 1000);
        }

        // --- Toast Notification Helper ---
        function showToast(msg) {
            const toast = document.createElement("div");
            toast.className = "fixed bottom-5 right-5 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-2xl text-xs z-50 flex items-center gap-3 border border-slate-700 transition-all animate-bounce";
            toast.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400 text-base"></i><span>${msg}</span>`;
            document.body.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }

        // --- Chart.js Initializations ---
        function initCharts() {
            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            trendChartInstance = new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: ['7일 전', '6일 전', '5일 전', '4일 전', '3일 전', '어제', '오늘'],
                    datasets: [
                        {
                            label: '입고 수량 (EA)',
                            data: [1200, 850, 1500, 920, 1100, 2400, inboundHistory.reduce((a,b)=>a+b.qty, 500)],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.3,
                            borderWidth: 2
                        },
                        {
                            label: '출고 수량 (EA)',
                            data: [950, 1100, 800, 1350, 1200, 1800, outboundHistory.reduce((a,b)=>a+b.qty, 170)],
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            fill: true,
                            tension: 0.3,
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'Pretendard', size: 11 } } }
                    },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { family: 'Pretendard', size: 10 } } },
                        x: { grid: { display: false }, ticks: { font: { family: 'Pretendard', size: 10 } } }
                    }
                }
            });

            const ctxCat = document.getElementById('categoryChart').getContext('2d');
            let catValues = { "원자재": 0, "부자재": 0, "전자부품": 0, "포장재": 0 };
            materialsData.forEach(m => {
                if (catValues[m.category] !== undefined) {
                    catValues[m.category] += (m.stock * m.price);
                }
            });

            categoryChartInstance = new Chart(ctxCat, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(catValues),
                    datasets: [{
                        data: Object.values(catValues),
                        backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#6366f1'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 10, font: { family: 'Pretendard', size: 10 } } }
                    },
                    cutout: '65%'
                }
            });
        }

        function updateCharts() {
            if (trendChartInstance) {
                trendChartInstance.data.datasets[0].data[6] = inboundHistory.reduce((a,b)=>a+b.qty, 0);
                trendChartInstance.data.datasets[1].data[6] = outboundHistory.reduce((a,b)=>a+b.qty, 0);
                trendChartInstance.update();
            }
            if (categoryChartInstance) {
                let catValues = { "원자재": 0, "부자재": 0, "전자부품": 0, "포장재": 0 };
                materialsData.forEach(m => {
                    if (catValues[m.category] !== undefined) {
                        catValues[m.category] += (m.stock * m.price);
                    }
                });
                categoryChartInstance.data.datasets[0].data = Object.values(catValues);
                categoryChartInstance.update();
            }
        }
    </script>
</body>
</html>
