<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP 연동 자재 관리 업무 자동화 대시보드</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts Pretendard -->
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Pretendard', 'sans-serif'],
                    },
                    colors: {
                        erp: {
                            50: '#f0f7ff',
                            100: '#e0effe',
                            500: '#2563eb',
                            600: '#1d4ed8',
                            700: '#1e40af',
                            800: '#1e3a8a',
                            900: '#0f172a',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Pretendard', sans-serif;
            background-color: #f8fafc;
        }
        .scrollbar-slim::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        .scrollbar-slim::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        .scrollbar-slim::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        .pulse-badge {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .4; }
        }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 antialiased min-h-screen flex flex-col md:flex-row">

    <!-- Sidebar Navigation -->
    <aside class="w-full md:w-64 bg-slate-900 text-slate-300 flex-shrink-0 flex flex-col justify-between shadow-xl">
        <div>
            <!-- Logo Header -->
            <div class="p-5 border-b border-slate-800 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="p-2 bg-blue-600 text-white rounded-lg shadow-lg">
                        <i class="fa-solid fa-boxes-stacked text-xl"></i>
                    </div>
                    <div>
                        <h1 class="font-bold text-white tracking-wide text-base">AUTO-ERP SCM</h1>
                        <p class="text-[11px] text-blue-400 font-medium">자재 관리 자동화 시스템</p>
                    </div>
                </div>
            </div>

            <!-- ERP Connection Widget -->
            <div class="m-4 p-3 bg-slate-800/80 rounded-xl border border-slate-700/60">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-slate-400">SAP ERP 연동 상태</span>
                    <span id="erpStatusBadge" class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 pulse-badge"></span> 동기화 완료
                    </span>
                </div>
                <div class="text-[11px] text-slate-400 space-y-1">
                    <div class="flex justify-between">
                        <span>마지막 연동:</span>
                        <span id="lastSyncTime" class="text-slate-200 font-mono">방금 전</span>
                    </div>
                    <div class="flex justify-between">
                        <span>대기 중인 트랜잭션:</span>
                        <span id="pendingTxCount" class="text-blue-400 font-bold font-mono">0 건</span>
                    </div>
                </div>
                <button onclick="triggerErpSync()" class="mt-3 w-full py-1.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2 shadow-sm">
                    <i id="syncIcon" class="fa-solid fa-rotate"></i>
                    <span>ERP 수동 실시간 동기화</span>
                </button>
            </div>

            <!-- Nav Links -->
            <nav class="px-3 py-2 space-y-1">
                <button onclick="switchTab('dashboard')" id="nav-dashboard" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all bg-blue-600 text-white shadow-md">
                    <i class="fa-solid fa-chart-pie w-5"></i>
                    <span>종합 대시보드</span>
                </button>
                <button onclick="switchTab('inbound')" id="nav-inbound" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-truck-ramp-box w-5"></i>
                    <span>자재 입고 관리</span>
                </button>
                <button onclick="switchTab('outbound')" id="nav-outbound" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-dolly w-5"></i>
                    <span>자재 출고 관리</span>
                </button>
                <button onclick="switchTab('inventory')" id="nav-inventory" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-warehouse w-5"></i>
                    <span>실시간 자재 현황</span>
                </button>
                <button onclick="switchTab('logs')" id="nav-logs" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
                    <i class="fa-solid fa-network-wired w-5"></i>
                    <span>ERP 연동 로그</span>
                </button>
            </nav>
        </div>

        <!-- User Info Footer -->
        <div class="p-4 border-t border-slate-800 flex items-center justify-between text-xs">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center font-bold text-white">
                    관
                </div>
                <div>
                    <p class="font-semibold text-white">김자재 관리자</p>
                    <p class="text-[10px] text-slate-400">구매자재 팀 / ERP 매니저</p>
                </div>
            </div>
            <span class="inline-block w-2 h-2 bg-emerald-500 rounded-full" title="온라인"></span>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto h-screen flex flex-col">
        <!-- Top Banner / Header -->
        <header class="bg-white border-b border-slate-200 px-6 py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 sticky top-0 z-10 shadow-sm">
            <div>
                <h2 id="pageTitle" class="text-xl font-bold text-slate-900 tracking-tight">ERP 연동 자재 관리 종합 대시보드</h2>
                <p id="pageDescription" class="text-xs text-slate-500 mt-0.5">실시간 자재 수급 상태 및 ERP 자동 전송 트랜잭션을 한눈에 확인합니다.</p>
            </div>
            <div class="flex items-center gap-3">
                <!-- Quick Actions -->
                <button onclick="openInboundModal()" class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5">
                    <i class="fa-solid fa-plus"></i> 입고 등록
                </button>
                <button onclick="openOutboundModal()" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5">
                    <i class="fa-solid fa-minus"></i> 출고 등록
                </button>
                <button onclick="simulateErpAutoOrder()" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5" title="재고 부족 품목에 대한 ERP 발주 자동 생성 시뮬레이션">
                    <i class="fa-solid fa-robot"></i> ERP 자동 발주
                </button>
            </div>
        </header>

        <!-- Dynamic Content Body -->
        <div class="p-6 space-y-6 flex-1">

            <!-- 1. TAB: DASHBOARD -->
            <div id="tab-content-dashboard" class="space-y-6">
                <!-- KPI Summary Grid -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">전체 관리 자재</p>
                                <h3 id="kpi-total-items" class="text-2xl font-bold text-slate-900 mt-1">0 품목</h3>
                                <p class="text-[11px] text-emerald-600 font-medium mt-1">
                                    <i class="fa-solid fa-arrow-up"></i> 정상 관리 중
                                </p>
                            </div>
                            <div class="p-3 bg-blue-50 text-blue-600 rounded-xl">
                                <i class="fa-solid fa-boxes-packing text-xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">금일 입고 건수</p>
                                <h3 id="kpi-inbound-today" class="text-2xl font-bold text-emerald-600 mt-1">0 건</h3>
                                <p id="kpi-inbound-amount" class="text-[11px] text-slate-500 mt-1">누적: 0 개</p>
                            </div>
                            <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
                                <i class="fa-solid fa-truck-arrow-right text-xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">금일 출고 건수</p>
                                <h3 id="kpi-outbound-today" class="text-2xl font-bold text-indigo-600 mt-1">0 건</h3>
                                <p id="kpi-outbound-amount" class="text-[11px] text-slate-500 mt-1">누적: 0 개</p>
                            </div>
                            <div class="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
                                <i class="fa-solid fa-truck-pickup text-xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">안전재고 부족 경고</p>
                                <h3 id="kpi-low-stock" class="text-2xl font-bold text-rose-600 mt-1">0 품목</h3>
                                <p class="text-[11px] text-rose-500 font-medium mt-1">
                                    <i class="fa-solid fa-triangle-exclamation"></i> ERP 자동 발주 검토 필요
                                </p>
                            </div>
                            <div class="p-3 bg-rose-50 text-rose-600 rounded-xl">
                                <i class="fa-solid fa-triangle-exclamation text-xl"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Inbound vs Outbound Trend Line Chart -->
                    <div class="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <h3 class="text-base font-bold text-slate-900">주간 자재 입·출고 동향 (ERP 연동 집계)</h3>
                                <p class="text-xs text-slate-500">최근 7일간 실시간 자동 동기화된 수량 흐름</p>
                            </div>
                            <span class="text-xs font-semibold bg-slate-100 px-2.5 py-1 rounded-md text-slate-600">단위: EA</span>
                        </div>
                        <div class="h-64 relative">
                            <canvas id="trendChart"></canvas>
                        </div>
                    </div>

                    <!-- Category Stock Distribution Chart -->
                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <h3 class="text-base font-bold text-slate-900">카테고리별 자재 자산 분포</h3>
                                <p class="text-xs text-slate-500">ERP 보유 평가 금액 기준 비율</p>
                            </div>
                        </div>
                        <div class="h-64 relative flex items-center justify-center">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Recent ERP Automation Logs Summary & Stock Alerts -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Low Stock Urgent Alert Table -->
                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <div class="flex items-center gap-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                                <h3 class="text-base font-bold text-slate-900">안전재고 미달 품목 (ERP 자동 발주 대상)</h3>
                            </div>
                            <button onclick="switchTab('inventory')" class="text-xs text-blue-600 hover:underline font-semibold">전체보기 &rarr;</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-xs text-left">
                                <thead class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                    <tr>
                                        <th class="p-2.5">자재코드</th>
                                        <th class="p-2.5">자재명</th>
                                        <th class="p-2.5 text-right">현재재고</th>
                                        <th class="p-2.5 text-right">안전재고</th>
                                        <th class="p-2.5 text-center">조치 status</th>
                                    </tr>
                                </thead>
                                <tbody id="dashboardLowStockBody" class="divide-y divide-slate-100">
                                    <!-- Dynamic Low Stock Row -->
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Live ERP Sync Log Stream -->
                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
                        <div class="flex items-center justify-between mb-4">
                            <div class="flex items-center gap-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-blue-500 pulse-badge"></span>
                                <h3 class="text-base font-bold text-slate-900">ERP 인터페이스 실시간 동기화 로그</h3>
                            </div>
                            <button onclick="switchTab('logs')" class="text-xs text-blue-600 hover:underline font-semibold">전체 로그 &rarr;</button>
                        </div>
                        <div id="dashboardLogsStream" class="flex-1 space-y-3 overflow-y-auto max-h-56 pr-1 text-xs scrollbar-slim">
                            <!-- Dynamic Logs Stream -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. TAB: INBOUND (자재 입고) -->
            <div id="tab-content-inbound" class="hidden space-y-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5">
                        <div>
                            <h3 class="text-lg font-bold text-slate-900">자재 입고 등록 및 내역</h3>
                            <p class="text-xs text-slate-500">입고 처리 시 ERP Inventory 마듈에 실시간 자동 기장됩니다.</p>
                        </div>
                        <div class="flex gap-2 w-full sm:w-auto">
                            <input type="text" id="inboundSearch" onkeyup="filterInboundTable()" placeholder="자재명/코드/공급업체 검색..." class="px-3 py-1.5 border border-slate-300 rounded-lg text-xs w-full sm:w-64 focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <button onclick="openInboundModal()" class="px-4 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700 transition-colors whitespace-nowrap">
                                <i class="fa-solid fa-plus mr-1"></i> 신규 입고
                            </button>
                        </div>
                    </div>
                    
                    <div class="overflow-x-auto rounded-xl border border-slate-200">
                        <table class="w-full text-xs text-left">
                            <thead class="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                                <tr>
                                    <th class="p-3">입고 번호</th>
                                    <th class="p-3">입고 일시</th>
                                    <th class="p-3">자재 코드 / 품명</th>
                                    <th class="p-3 text-right">입고 수량</th>
                                    <th class="p-3">공급업체</th>
                                    <th class="p-3">보관 위치</th>
                                    <th class="p-3 text-center">ERP 전송 상태</th>
                                </tr>
                            </thead>
                            <tbody id="inboundTableBody" class="divide-y divide-slate-100">
                                <!-- Dynamic Inbound History -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 3. TAB: OUTBOUND (자재 출고) -->
            <div id="tab-content-outbound" class="hidden space-y-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5">
                        <div>
                            <h3 class="text-lg font-bold text-slate-900">자재 출고 요청 및 불출 내역</h3>
                            <p class="text-xs text-slate-500">생산/현장 출고 요청을 승인하고 ERP 비용 계정에 자동 매핑합니다.</p>
                        </div>
                        <div class="flex gap-2 w-full sm:w-auto">
                            <input type="text" id="outboundSearch" onkeyup="filterOutboundTable()" placeholder="자재명/부서/요청자 검색..." class="px-3 py-1.5 border border-slate-300 rounded-lg text-xs w-full sm:w-64 focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <button onclick="openOutboundModal()" class="px-4 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition-colors whitespace-nowrap">
                                <i class="fa-solid fa-minus mr-1"></i> 신규 출고
                            </button>
                        </div>
                    </div>

                    <div class="overflow-x-auto rounded-xl border border-slate-200">
                        <table class="w-full text-xs text-left">
                            <thead class="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                                <tr>
                                    <th class="p-3">출고 번호</th>
                                    <th class="p-3">출고 일시</th>
                                    <th class="p-3">자재 코드 / 품명</th>
                                    <th class="p-3 text-right">출고 수량</th>
                                    <th class="p-3">사용 부서 / 프로젝트</th>
                                    <th class="p-3">불출 요청자</th>
                                    <th class="p-3 text-center">ERP 정산 상태</th>
                                </tr>
                            </thead>
                            <tbody id="outboundTableBody" class="divide-y divide-slate-100">
                                <!-- Dynamic Outbound History -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 4. TAB: REAL-TIME INVENTORY (실시간 자재 현황) -->
            <div id="tab-content-inventory" class="hidden space-y-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5">
                        <div>
                            <h3 class="text-lg font-bold text-slate-900">실시간 통합 자재 재고 현황</h3>
                            <p class="text-xs text-slate-500">창고 실물 수량과 ERP 장부 수량이 실시간 동기화된 데이터입니다.</p>
                        </div>
                        <div class="flex flex-wrap gap-2">
                            <select id="categoryFilter" onchange="renderInventoryTable()" class="px-3 py-1.5 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="ALL">전체 카테고리</option>
                                <option value="원자재">원자재</option>
                                <option value="부자재">부자재</option>
                                <option value="전자부품">전자부품</option>
                                <option value="포장재">포장재</option>
                            </select>
                            <select id="stockStatusFilter" onchange="renderInventoryTable()" class="px-3 py-1.5 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="ALL">전체 재고 상태</option>
                                <option value="NORMAL">정상</option>
                                <option value="LOW">안전재고 미달</option>
                            </select>
                            <input type="text" id="inventorySearch" onkeyup="renderInventoryTable()" placeholder="자재명 또는 코드 검색..." class="px-3 py-1.5 border border-slate-300 rounded-lg text-xs w-48 focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>

                    <div class="overflow-x-auto rounded-xl border border-slate-200">
                        <table class="w-full text-xs text-left">
                            <thead class="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                                <tr>
                                    <th class="p-3">자재 코드</th>
                                    <th class="p-3">자재명</th>
                                    <th class="p-3">분류</th>
                                    <th class="p-3 text-right">현재 재고</th>
                                    <th class="p-3 text-right">안전 재고</th>
                                    <th class="p-3 text-right">단가 (원)</th>
                                    <th class="p-3 text-right">총 평가액 (원)</th>
                                    <th class="p-3">보관 랙(Rack)</th>
                                    <th class="p-3 text-center">상태</th>
                                    <th class="p-3 text-center">ERP 작업</th>
                                </tr>
                            </thead>
                            <tbody id="inventoryTableBody" class="divide-y divide-slate-100">
                                <!-- Dynamic Inventory Rows -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 5. TAB: LOGS (ERP 연동 로그) -->
            <div id="tab-content-logs" class="hidden space-y-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                    <div class="flex justify-between items-center mb-4">
                        <div>
                            <h3 class="text-lg font-bold text-slate-900">ERP 인터페이스 송수신 로그 (SAP / MES / WMS)</h3>
                            <p class="text-xs text-slate-500">자재 관리에 따른 자동 API 요청 및 수신 응답 히스토리</p>
                        </div>
                        <button onclick="clearLogs()" class="px-3 py-1.5 text-xs text-slate-500 border border-slate-300 rounded-lg hover:bg-slate-50">로그 초기화</button>
                    </div>

                    <div class="bg-slate-900 text-slate-200 font-mono text-xs p-4 rounded-xl max-h-[550px] overflow-y-auto scrollbar-slim space-y-2 border border-slate-800" id="fullLogContainer">
                        <!-- Dynamic Full Logs -->
                    </div>
                </div>
            </div>

        </div>
    </main>

    <!-- Modal 1: Inbound Form Modal -->
    <div id="inboundModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden">
            <div class="px-6 py-4 bg-emerald-600 text-white flex justify-between items-center">
                <h3 class="font-bold text-base flex items-center gap-2"><i class="fa-solid fa-truck-ramp-box"></i> 신규 자재 입고 처리</h3>
                <button onclick="closeInboundModal()" class="text-white/80 hover:text-white text-lg">&times;</button>
            </div>
            <form id="inboundForm" onsubmit="handleInboundSubmit(event)" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">입고 자재 선택</label>
                    <select id="inboundMaterialCode" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 outline-none">
                        <!-- Options generated dynamically -->
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">입고 수량</label>
                    <input type="number" id="inboundQty" min="1" required placeholder="수량 입력" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">공급 업체 (Vendor)</label>
                    <input type="text" id="inboundVendor" required placeholder="예: (주)한국소재산업" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">입고 창고/랙 위치</label>
                    <input type="text" id="inboundLocation" placeholder="예: A1-Zone-04" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 outline-none">
                </div>
                <div class="p-3 bg-emerald-50 rounded-lg border border-emerald-100 text-[11px] text-emerald-800 flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-emerald-600"></i>
                    <span>등록 즉시 ERP 재고 모듈에 MIGO 입고 문서가 자동 생성됩니다.</span>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeInboundModal()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">취소</button>
                    <button type="submit" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-md transition-all">입고 확정 및 ERP 전송</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal 2: Outbound Form Modal -->
    <div id="outboundModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden">
            <div class="px-6 py-4 bg-indigo-600 text-white flex justify-between items-center">
                <h3 class="font-bold text-base flex items-center gap-2"><i class="fa-solid fa-dolly"></i> 신규 자재 출고 불출</h3>
                <button onclick="closeOutboundModal()" class="text-white/80 hover:text-white text-lg">&times;</button>
            </div>
            <form id="outboundForm" onsubmit="handleOutboundSubmit(event)" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">출고 대상 자재</label>
                    <select id="outboundMaterialCode" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                        <!-- Options generated dynamically -->
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">출고 수량</label>
                    <input type="number" id="outboundQty" min="1" required placeholder="수량 입력" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">사용 부서 / 생산 라인</label>
                    <input type="text" id="outboundDept" required placeholder="예: 조립 2라인 / 제조팀" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">불출 요청자</label>
                    <input type="text" id="outboundRequester" required placeholder="예: 박생산 과장" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div class="p-3 bg-indigo-50 rounded-lg border border-indigo-100 text-[11px] text-indigo-800 flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-indigo-600"></i>
                    <span>출고 시 해당 생산 코스트센터로 비용 처리가 자동 계상됩니다.</span>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeOutboundModal()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">취소</button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-md transition-all">출고 처리 및 ERP 반영</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Notification Toast Container -->
    <div id="toastContainer" class="fixed bottom-5 right-5 z-50 space-y-2"></div>

    <script>
        // =========================================================================
        // DUMMY DATA STATE
        // =========================================================================
        let materials = [
            { code: "MAT-1001", name: "스테인리스 강판 2mm", category: "원자재", stock: 450, safetyStock: 150, unit: "장", unitPrice: 85000, location: "A1-Rack-01" },
            { code: "MAT-1002", name: "알루미늄 압출 프레임", category: "원자재", stock: 85, safetyStock: 100, unit: "M", unitPrice: 32000, location: "A1-Rack-03" },
            { code: "MAT-2001", name: "고성능 서보 모터 400W", category: "전자부품", stock: 32, safetyStock: 40, unit: "EA", unitPrice: 240000, location: "B2-Cabinet-01" },
            { code: "MAT-2002", name: "PLC 제어 모듈 FX-5U", category: "전자부품", stock: 18, safetyStock: 15, unit: "EA", unitPrice: 480000, location: "B2-Cabinet-02" },
            { code: "MAT-3001", name: "산업용 육각 볼트 M8", category: "부자재", stock: 12500, safetyStock: 3000, unit: "개", unitPrice: 150, location: "C1-Bin-12" },
            { code: "MAT-3002", name: "내열 내유 실리콘 가스켓", category: "부자재", stock: 180, safetyStock: 250, unit: "개", unitPrice: 4500, location: "C1-Bin-15" },
            { code: "MAT-4001", name: "수송용 완충 파렛트 박스", category: "포장재", stock: 420, safetyStock: 200, unit: "EA", unitPrice: 18000, location: "D-Warehouse-01" },
            { code: "MAT-4002", name: "친환경 스트레치 필름", category: "포장재", stock: 65, safetyStock: 80, unit: "롤", unitPrice: 22000, location: "D-Warehouse-02" }
        ];

        let inbounds = [
            { id: "IN-20260729-01", date: "2026-07-29 09:15", code: "MAT-1001", name: "스테인리스 강판 2mm", qty: 100, vendor: "(주)동아제강", location: "A1-Rack-01", erpStatus: "Synced" },
            { id: "IN-20260729-02", date: "2026-07-29 11:30", code: "MAT-3001", name: "산업용 육각 볼트 M8", qty: 5000, vendor: "태양파스너(주)", location: "C1-Bin-12", erpStatus: "Synced" },
            { id: "IN-20260728-01", date: "2026-07-28 14:20", code: "MAT-2002", name: "PLC 제어 모듈 FX-5U", qty: 10, vendor: "미츠비시 오토메이션", location: "B2-Cabinet-02", erpStatus: "Synced" }
        ];

        let outbounds = [
            { id: "OUT-20260729-01", date: "2026-07-29 10:05", code: "MAT-2001", name: "고성능 서보 모터 400W", qty: 5, dept: "자동화 1라인", requester: "이현장 과장", erpStatus: "Settled" },
            { id: "OUT-20260729-02", date: "2026-07-29 13:45", code: "MAT-1002", name: "알루미늄 압출 프레임", qty: 30, dept: "가공조립 2팀", requester: "최조립 대리", erpStatus: "Settled" },
            { id: "OUT-20260728-02", date: "2026-07-28 16:10", code: "MAT-3002", name: "내열 내유 실리콘 가스켓", qty: 50, dept: "설비보전팀", requester: "김정비 주임", erpStatus: "Settled" }
        ];

        let logs = [
            { time: "15:20:11", type: "INFO", text: "SAP ERP RFC_READ_TABLE 실행 완료 - 자재 마스터 수신" },
            { time: "13:45:02", type: "SUCCESS", text: "출고 건 [OUT-20260729-02] SAP CO 모듈 비용계정(200301) 정산 연동 완료" },
            { time: "11:30:15", type: "SUCCESS", text: "입고 건 [IN-20260729-02] MM 모듈 입고문서 #500049281 자동 생성" },
            { time: "09:15:40", type: "SUCCESS", text: "입고 건 [IN-20260729-01] MM 모듈 입고문서 #500049280 자동 생성" },
            { time: "09:00:00", type: "SYSTEM", text: "ERP 오토메이션 스케줄러 배치 동작 - 이상 무" }
        ];

        let trendChartInstance = null;
        let categoryChartInstance = null;

        // =========================================================================
        // INITIALIZATION
        // =========================================================================
        window.addEventListener('DOMContentLoaded', () => {
            initSelectOptions();
            updateDashboardKPIs();
            renderDashboardTablesAndLogs();
            renderInboundTable();
            renderOutboundTable();
            renderInventoryTable();
            renderFullLogs();
            initCharts();
        });

        // Navigation Handler
        function switchTab(tabName) {
            const tabs = ['dashboard', 'inbound', 'outbound', 'inventory', 'logs'];
            tabs.forEach(t => {
                const content = document.getElementById(`tab-content-${t}`);
                const navBtn = document.getElementById(`nav-${t}`);
                if (t === tabName) {
                    content.classList.remove('hidden');
                    navBtn.classList.add('bg-blue-600', 'text-white', 'shadow-md');
                    navBtn.classList.remove('hover:bg-slate-800', 'text-slate-400');
                } else {
                    content.classList.add('hidden');
                    navBtn.classList.remove('bg-blue-600', 'text-white', 'shadow-md');
                    navBtn.classList.add('hover:bg-slate-800', 'text-slate-400');
                }
            });

            // Update Page Headers
            const titleMap = {
                'dashboard': 'ERP 연동 자재 관리 종합 대시보드',
                'inbound': '자재 입고 처리 및 ERP 전송 관리',
                'outbound': '자재 출고 불출 및 코스트센터 정산',
                'inventory': '실시간 통합 자재 재고 현황 및 발주 관리',
                'logs': 'ERP 인터페이스 실시간 연동 로그'
            };
            const descMap = {
                'dashboard': '실시간 자재 수급 상태 및 ERP 자동 전송 트랜잭션을 한눈에 확인합니다.',
                'inbound': '입고 등록 시 SAP/ERP 자재 모듈(MM)로 입고 전표가 즉시 전송됩니다.',
                'outbound': '출고 불출 시 해당 생산 부서 비용 계정으로 실시간 자동 매핑됩니다.',
                'inventory': '안전재고 미달 품목 자동 감지 및 ERP 구매요청서(PR) 생성을 지원합니다.',
                'logs': 'SAP/ERP 시스템 간 API 통신 및 웹훅 트리거 이력을 모니터링합니다.'
            };

            document.getElementById('pageTitle').innerText = titleMap[tabName];
            document.getElementById('pageDescription').innerText = descMap[tabName];
        }

        // =========================================================================
        // MODALS & INPUT HANDLERS
        // =========================================================================
        function initSelectOptions() {
            const inboundSelect = document.getElementById('inboundMaterialCode');
            const outboundSelect = document.getElementById('outboundMaterialCode');

            inboundSelect.innerHTML = materials.map(m => `<option value="${m.code}">${m.code} - ${m.name} (현재: ${m.stock} ${m.unit})</option>`).join('');
            outboundSelect.innerHTML = materials.map(m => `<option value="${m.code}">${m.code} - ${m.name} (현재: ${m.stock} ${m.unit})</option>`).join('');
        }

        function openInboundModal() {
            initSelectOptions();
            document.getElementById('inboundModal').classList.remove('hidden');
            document.getElementById('inboundModal').classList.add('flex');
        }

        function closeInboundModal() {
            document.getElementById('inboundModal').classList.add('hidden');
            document.getElementById('inboundModal').classList.remove('flex');
        }

        function openOutboundModal() {
            initSelectOptions();
            document.getElementById('outboundModal').classList.remove('hidden');
            document.getElementById('outboundModal').classList.add('flex');
        }

        function closeOutboundModal() {
            document.getElementById('outboundModal').classList.add('hidden');
            document.getElementById('outboundModal').classList.remove('flex');
        }

        function handleInboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById('inboundMaterialCode').value;
            const qty = parseInt(document.getElementById('inboundQty').value);
            const vendor = document.getElementById('inboundVendor').value;
            const location = document.getElementById('inboundLocation').value || "메인 창고";

            const mat = materials.find(m => m.code === code);
            if (!mat) return;

            mat.stock += qty;
            const now = new Date();
            const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
            const newId = `IN-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${Math.floor(Math.random()*90+10)}`;

            inbounds.unshift({
                id: newId,
                date: timeStr,
                code: mat.code,
                name: mat.name,
                qty: qty,
                vendor: vendor,
                location: location,
                erpStatus: "Synced"
            });

            addLog("SUCCESS", `[입고 연동] ${mat.name} (${qty} ${mat.unit}) 입고 완료 -> ERP MM 문서 자동 생성`);
            showToast(`입고 성공! ${mat.name} +${qty} ${mat.unit} (ERP 자동 저장됨)`, 'emerald');

            closeInboundModal();
            refreshSystem();
            document.getElementById('inboundForm').reset();
        }

        function handleOutboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById('outboundMaterialCode').value;
            const qty = parseInt(document.getElementById('outboundQty').value);
            const dept = document.getElementById('outboundDept').value;
            const requester = document.getElementById('outboundRequester').value;

            const mat = materials.find(m => m.code === code);
            if (!mat) return;

            if (mat.stock < qty) {
                showToast(`출고 실패! 재고 수량이 부족합니다. (현재: ${mat.stock} ${mat.unit})`, 'rose');
                return;
            }

            mat.stock -= qty;
            const now = new Date();
            const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
            const newId = `OUT-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${Math.floor(Math.random()*90+10)}`;

            outbounds.unshift({
                id: newId,
                date: timeStr,
                code: mat.code,
                name: mat.name,
                qty: qty,
                dept: dept,
                requester: requester,
                erpStatus: "Settled"
            });

            addLog("SUCCESS", `[출고 연동] ${mat.name} (${qty} ${mat.unit}) 불출 완료 -> ERP CO 코스트센터 매핑 완료`);
            showToast(`출고 완료! ${mat.name} -${qty} ${mat.unit} (ERP 비용 매핑됨)`, 'indigo');

            // Safety Stock Alert Trigger
            if (mat.stock < mat.safetyStock) {
                setTimeout(() => {
                    addLog("WARN", `[안전재고 미달] ${mat.name} 현재 재고 ${mat.stock} < 안전재고 ${mat.safetyStock}. ERP 발주 검토 권장`);
                    showToast(`⚠️ ${mat.name} 재고가 안전 수준 이하로 떨어졌습니다!`, 'amber');
                }, 800);
            }

            closeOutboundModal();
            refreshSystem();
            document.getElementById('outboundForm').reset();
        }

        // =========================================================================
        // AUTOMATION & SIMULATION ENGINE
        // =========================================================================
        function triggerErpSync() {
            const icon = document.getElementById('syncIcon');
            const badge = document.getElementById('erpStatusBadge');
            icon.classList.add('fa-spin');
            
            badge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30";
            badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-blue-400 mr-1.5 pulse-badge"></span> 동기화 중...`;

            setTimeout(() => {
                icon.classList.remove('fa-spin');
                badge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30";
                badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 pulse-badge"></span> 동기화 완료`;

                const now = new Date();
                const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
                document.getElementById('lastSyncTime').innerText = timeStr;

                addLog("INFO", "SAP ERP 전체 자재 원장 및 실시간 수량 동기화 완료 (HTTP 200 OK)");
                showToast("SAP ERP 수동 실시간 동기화가 성공적으로 수행되었습니다.", 'blue');
            }, 1200);
        }

        function simulateErpAutoOrder() {
            const lowStockItems = materials.filter(m => m.stock < m.safetyStock);
            if (lowStockItems.length === 0) {
                showToast("현재 안전재고 미달 품목이 없어 자동 발주가 필요하지 않습니다.", "emerald");
                return;
            }

            lowStockItems.forEach(item => {
                const reqQty = (item.safetyStock * 2) - item.stock;
                addLog("AUTO", `[ERP 자동 발주] ${item.name} (${item.code}) 구매요청서(PR-2026-${Math.floor(Math.random()*8000+1000)}) 자동 발행 (요청수량: ${reqQty} ${item.unit})`);
            });

            showToast(`ERP 자동화: ${lowStockItems.length}개 품목에 대한 전자 구매요청서(PR)가 생성되었습니다.`, "amber");
            refreshSystem();
        }

        function addLog(type, text) {
            const now = new Date();
            const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
            logs.unshift({ time: timeStr, type: type, text: text });
            renderDashboardTablesAndLogs();
            renderFullLogs();
        }

        function clearLogs() {
            logs = [];
            renderDashboardTablesAndLogs();
            renderFullLogs();
        }

        // =========================================================================
        // RENDERING FUNCTIONS
        // =========================================================================
        function refreshSystem() {
            updateDashboardKPIs();
            renderDashboardTablesAndLogs();
            renderInboundTable();
            renderOutboundTable();
            renderInventoryTable();
            updateCharts();
        }

        function updateDashboardKPIs() {
            document.getElementById('kpi-total-items').innerText = `${materials.length} 품목`;
            
            // Today's Inbound Count
            const todayStr = "2026-07-29";
            const todayInbounds = inbounds.filter(i => i.date.startsWith(todayStr));
            const totalInboundQty = todayInbounds.reduce((sum, i) => sum + i.qty, 0);
            document.getElementById('kpi-inbound-today').innerText = `${todayInbounds.length} 건`;
            document.getElementById('kpi-inbound-amount').innerText = `금일 누적: ${totalInboundQty.toLocaleString()} 개`;

            // Today's Outbound Count
            const todayOutbounds = outbounds.filter(o => o.date.startsWith(todayStr));
            const totalOutboundQty = todayOutbounds.reduce((sum, o) => sum + o.qty, 0);
            document.getElementById('kpi-outbound-today').innerText = `${todayOutbounds.length} 건`;
            document.getElementById('kpi-outbound-amount').innerText = `금일 누적: ${totalOutboundQty.toLocaleString()} 개`;

            // Low Stock Count
            const lowStockList = materials.filter(m => m.stock < m.safetyStock);
            document.getElementById('kpi-low-stock').innerText = `${lowStockList.length} 품목`;
        }

        function renderDashboardTablesAndLogs() {
            // Low Stock Table
            const lowStockBody = document.getElementById('dashboardLowStockBody');
            const lowStockItems = materials.filter(m => m.stock < m.safetyStock);

            if (lowStockItems.length === 0) {
                lowStockBody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-slate-400">모든 자재가 안전재고 이상을 유지하고 있습니다.</td></tr>`;
            } else {
                lowStockBody.innerHTML = lowStockItems.map(item => `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-2.5 font-mono text-slate-600 font-semibold">${item.code}</td>
                        <td class="p-2.5 font-semibold text-slate-800">${item.name}</td>
                        <td class="p-2.5 text-right font-bold text-rose-600">${item.stock.toLocaleString()} ${item.unit}</td>
                        <td class="p-2.5 text-right text-slate-500">${item.safetyStock.toLocaleString()} ${item.unit}</td>
                        <td class="p-2.5 text-center">
                            <button onclick="simulateSingleAutoOrder('${item.code}')" class="px-2 py-1 bg-amber-500 hover:bg-amber-600 text-white rounded text-[10px] font-bold shadow-sm">
                                ERP 발주 생성
                            </button>
                        </td>
                    </tr>
                `).join('');
            }

            // Live Stream Logs (Last 5)
            const streamContainer = document.getElementById('dashboardLogsStream');
            streamContainer.innerHTML = logs.slice(0, 5).map(log => {
                let badgeClass = "bg-blue-500/10 text-blue-600 border-blue-200";
                if(log.type === "SUCCESS") badgeClass = "bg-emerald-500/10 text-emerald-600 border-emerald-200";
                if(log.type === "WARN" || log.type === "AUTO") badgeClass = "bg-amber-500/10 text-amber-600 border-amber-200";

                return `
                    <div class="flex items-start gap-2.5 p-2 bg-slate-50 rounded-lg border border-slate-100 text-[11px]">
                        <span class="font-mono text-slate-400 shrink-0">${log.time}</span>
                        <span class="px-1.5 py-0.5 rounded text-[9px] font-bold border ${badgeClass} shrink-0">${log.type}</span>
                        <span class="text-slate-700 truncate">${log.text}</span>
                    </div>
                `;
            }).join('');
        }

        function simulateSingleAutoOrder(code) {
            const item = materials.find(m => m.code === code);
            if(!item) return;
            const reqQty = (item.safetyStock * 2) - item.stock;
            addLog("AUTO", `[ERP 수동 수발주] ${item.name} PR-2026-${Math.floor(Math.random()*8000+1000)} 구매요청서 발송 (${reqQty} ${item.unit})`);
            showToast(`${item.name}에 대한 ERP 발주 생성 요청이 제출되었습니다.`, "emerald");
        }

        function renderInboundTable() {
            const body = document.getElementById('inboundTableBody');
            body.innerHTML = inbounds.map(item => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="p-3 font-mono font-medium text-slate-500">${item.id}</td>
                    <td class="p-3 font-mono text-slate-600">${item.date}</td>
                    <td class="p-3">
                        <span class="font-semibold text-slate-800 block">${item.name}</span>
                        <span class="text-[10px] text-slate-400 font-mono">${item.code}</span>
                    </td>
                    <td class="p-3 text-right font-bold text-emerald-600">+${item.qty.toLocaleString()}</td>
                    <td class="p-3 text-slate-600">${item.vendor}</td>
                    <td class="p-3 text-slate-500">${item.location}</td>
                    <td class="p-3 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-600 border border-emerald-200">
                            <i class="fa-solid fa-check mr-1"></i> ERP 연동됨
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        function filterInboundTable() {
            const query = document.getElementById('inboundSearch').value.toLowerCase();
            const filtered = inbounds.filter(i => i.name.toLowerCase().includes(query) || i.code.toLowerCase().includes(query) || i.vendor.toLowerCase().includes(query));
            
            const body = document.getElementById('inboundTableBody');
            body.innerHTML = filtered.map(item => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="p-3 font-mono font-medium text-slate-500">${item.id}</td>
                    <td class="p-3 font-mono text-slate-600">${item.date}</td>
                    <td class="p-3">
                        <span class="font-semibold text-slate-800 block">${item.name}</span>
                        <span class="text-[10px] text-slate-400 font-mono">${item.code}</span>
                    </td>
                    <td class="p-3 text-right font-bold text-emerald-600">+${item.qty.toLocaleString()}</td>
                    <td class="p-3 text-slate-600">${item.vendor}</td>
                    <td class="p-3 text-slate-500">${item.location}</td>
                    <td class="p-3 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-600 border border-emerald-200">
                            <i class="fa-solid fa-check mr-1"></i> ERP 연동됨
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        function renderOutboundTable() {
            const body = document.getElementById('outboundTableBody');
            body.innerHTML = outbounds.map(item => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="p-3 font-mono font-medium text-slate-500">${item.id}</td>
                    <td class="p-3 font-mono text-slate-600">${item.date}</td>
                    <td class="p-3">
                        <span class="font-semibold text-slate-800 block">${item.name}</span>
                        <span class="text-[10px] text-slate-400 font-mono">${item.code}</span>
                    </td>
                    <td class="p-3 text-right font-bold text-indigo-600">-${item.qty.toLocaleString()}</td>
                    <td class="p-3 text-slate-600">${item.dept}</td>
                    <td class="p-3 text-slate-500">${item.requester}</td>
                    <td class="p-3 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-600 border border-indigo-200">
                            <i class="fa-solid fa-receipt mr-1"></i> CO 정산완료
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        function filterOutboundTable() {
            const query = document.getElementById('outboundSearch').value.toLowerCase();
            const filtered = outbounds.filter(o => o.name.toLowerCase().includes(query) || o.code.toLowerCase().includes(query) || o.dept.toLowerCase().includes(query) || o.requester.toLowerCase().includes(query));
            
            const body = document.getElementById('outboundTableBody');
            body.innerHTML = filtered.map(item => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="p-3 font-mono font-medium text-slate-500">${item.id}</td>
                    <td class="p-3 font-mono text-slate-600">${item.date}</td>
                    <td class="p-3">
                        <span class="font-semibold text-slate-800 block">${item.name}</span>
                        <span class="text-[10px] text-slate-400 font-mono">${item.code}</span>
                    </td>
                    <td class="p-3 text-right font-bold text-indigo-600">-${item.qty.toLocaleString()}</td>
                    <td class="p-3 text-slate-600">${item.dept}</td>
                    <td class="p-3 text-slate-500">${item.requester}</td>
                    <td class="p-3 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-600 border border-indigo-200">
                            <i class="fa-solid fa-receipt mr-1"></i> CO 정산완료
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        function renderInventoryTable() {
            const catFilter = document.getElementById('categoryFilter').value;
            const stockFilter = document.getElementById('stockStatusFilter').value;
            const searchQuery = document.getElementById('inventorySearch').value.toLowerCase();

            let filtered = materials.filter(m => {
                const matchesCat = (catFilter === 'ALL' || m.category === catFilter);
                const matchesStock = (stockFilter === 'ALL') || (stockFilter === 'LOW' && m.stock < m.safetyStock) || (stockFilter === 'NORMAL' && m.stock >= m.safetyStock);
                const matchesSearch = m.name.toLowerCase().includes(searchQuery) || m.code.toLowerCase().includes(searchQuery);
                return matchesCat && matchesStock && matchesSearch;
            });

            const body = document.getElementById('inventoryTableBody');
            body.innerHTML = filtered.map(item => {
                const totalValue = item.stock * item.unitPrice;
                const isLow = item.stock < item.safetyStock;
                const statusBadge = isLow 
                    ? `<span class="px-2 py-0.5 bg-rose-100 text-rose-700 font-bold text-[10px] rounded-full border border-rose-200">부족 (경고)</span>`
                    : `<span class="px-2 py-0.5 bg-emerald-100 text-emerald-700 font-bold text-[10px] rounded-full border border-emerald-200">정상</span>`;

                return `
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="p-3 font-mono font-bold text-slate-600">${item.code}</td>
                        <td class="p-3 font-semibold text-slate-900">${item.name}</td>
                        <td class="p-3 text-slate-500">${item.category}</td>
                        <td class="p-3 text-right font-bold ${isLow ? 'text-rose-600' : 'text-slate-800'}">${item.stock.toLocaleString()} ${item.unit}</td>
                        <td class="p-3 text-right text-slate-400 font-mono">${item.safetyStock.toLocaleString()} ${item.unit}</td>
                        <td class="p-3 text-right font-mono text-slate-600">₩${item.unitPrice.toLocaleString()}</td>
                        <td class="p-3 text-right font-mono font-bold text-slate-900">₩${totalValue.toLocaleString()}</td>
                        <td class="p-3 text-slate-500 font-mono">${item.location}</td>
                        <td class="p-3 text-center">${statusBadge}</td>
                        <td class="p-3 text-center">
                            <button onclick="adjustStockModal('${item.code}')" class="text-xs text-blue-600 hover:underline font-semibold">수량 조정</button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function adjustStockModal(code) {
            const item = materials.find(m => m.code === code);
            if (!item) return;

            const newStockStr = prompt(`[${item.name}] 재고 조정 수량을 입력하세요:`, item.stock);
            if (newStockStr !== null) {
                const newStock = parseInt(newStockStr);
                if (!isNaN(newStock) && newStock >= 0) {
                    const diff = newStock - item.stock;
                    item.stock = newStock;
                    addLog("WARN", `[실물 실사 조정] ${item.name} 수량 변경 (${diff >= 0 ? '+' : ''}${diff}) -> ERP 재무 조정 반영`);
                    showToast(`${item.name} 재고가 ${newStock} ${item.unit}(으)로 조정되었습니다.`, 'blue');
                    refreshSystem();
                }
            }
        }

        function renderFullLogs() {
            const container = document.getElementById('fullLogContainer');
            container.innerHTML = logs.map(log => {
                let colorClass = "text-slate-300";
                if(log.type === "SUCCESS") colorClass = "text-emerald-400";
                if(log.type === "WARN") colorClass = "text-amber-400";
                if(log.type === "AUTO") colorClass = "text-indigo-400";

                return `
                    <div class="flex items-start gap-3 border-b border-slate-800/60 pb-1.5">
                        <span class="text-slate-500 select-none">${log.time}</span>
                        <span class="font-bold uppercase ${colorClass} w-16 text-right">[${log.type}]</span>
                        <span class="flex-1 ${colorClass}">${log.text}</span>
                    </div>
                `;
            }).join('');
        }

        // =========================================================================
        // CHART VISUALIZATION (Chart.js)
        // =========================================================================
        function initCharts() {
            // 1. Inbound vs Outbound Trend Line Chart
            const trendCtx = document.getElementById('trendChart').getContext('2d');
            trendChartInstance = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: ['7/23(목)', '7/24(금)', '7/25(토)', '7/26(일)', '7/27(월)', '7/28(화)', '7/29(수)'],
                    datasets: [
                        {
                            label: '입고 수량',
                            data: [320, 450, 120, 80, 600, 510, 5100],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.08)',
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2
                        },
                        {
                            label: '출고 수량',
                            data: [280, 390, 150, 40, 480, 420, 35],
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.08)',
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { font: { family: 'Pretendard', size: 11 } } }
                    },
                    scales: {
                        y: { grid: { color: '#f1f5f9' }, ticks: { font: { family: 'Pretendard', size: 10 } } },
                        x: { grid: { display: false }, ticks: { font: { family: 'Pretendard', size: 10 } } }
                    }
                }
            });

            // 2. Category Doughnut Chart
            const catCtx = document.getElementById('categoryChart').getContext('2d');
            const categoryData = getCategoryAssetDistribution();

            categoryChartInstance = new Chart(catCtx, {
                type: 'doughnut',
                data: {
                    labels: categoryData.labels,
                    datasets: [{
                        data: categoryData.data,
                        backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { font: { family: 'Pretendard', size: 11 }, boxWidth: 12 } }
                    },
                    cutout: '65%'
                }
            });
        }

        function getCategoryAssetDistribution() {
            const catTotals = {};
            materials.forEach(m => {
                const totalVal = m.stock * m.unitPrice;
                catTotals[m.category] = (catTotals[m.category] || 0) + totalVal;
            });
            return {
                labels: Object.keys(catTotals),
                data: Object.values(catTotals)
            };
        }

        function updateCharts() {
            if (categoryChartInstance) {
                const categoryData = getCategoryAssetDistribution();
                categoryChartInstance.data.labels = categoryData.labels;
                categoryChartInstance.data.datasets[0].data = categoryData.data;
                categoryChartInstance.update();
            }
        }

        // =========================================================================
        // UTILS: TOAST NOTIFICATIONS
        // =========================================================================
        function showToast(message, color = 'blue') {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            
            const colorClasses = {
                emerald: 'bg-emerald-800 text-white border-emerald-600',
                indigo: 'bg-indigo-800 text-white border-indigo-600',
                amber: 'bg-amber-800 text-white border-amber-600',
                rose: 'bg-rose-800 text-white border-rose-600',
                blue: 'bg-slate-800 text-white border-slate-600'
            };

            toast.className = `p-3.5 rounded-xl shadow-2xl border text-xs font-semibold flex items-center gap-2 transform transition-all duration-300 translate-y-4 opacity-0 ${colorClasses[color] || colorClasses.blue}`;
            toast.innerHTML = `<i class="fa-solid fa-circle-info text-sm"></i> <span>${message}</span>`;

            container.appendChild(toast);

            setTimeout(() => {
                toast.classList.remove('translate-y-4', 'opacity-0');
            }, 50);

            setTimeout(() => {
                toast.classList.add('opacity-0', 'translate-y-2');
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }
    </script>
</body>
</html>
