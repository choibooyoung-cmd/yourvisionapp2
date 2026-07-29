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
                            <p class="text-xs text-slate-500">입고 처리 시 ERP Inventory 모듈에 실시간 자동 기장됩니다.</p>
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
                    <label class="block text-xs font-bold text-slate-700 mb-1">출고 자재 선택</label>
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
                    <input type="text" id="outboundDept" required placeholder="예: 생산1팀 (Line-B)" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">불출 요청자</label>
                    <input type="text" id="outboundRequester" required placeholder="예: 이생산 대리" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div class="p-3 bg-indigo-50 rounded-lg border border-indigo-100 text-[11px] text-indigo-800 flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-indigo-600"></i>
                    <span>출고 승인 시 해당 부서 Cost Center로 ERP 자재비용이 자동 이전 계상됩니다.</span>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeOutboundModal()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">취소</button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-md transition-all">출고 승인 및 ERP 전송</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Application Script -->
    <script>
        // Initial Material Data State
        let materials = [
            { code: 'MAT-1001', name: '고강도 알루미늄 프레임 A', category: '원자재', stock: 450, safeStock: 200, unitPrice: 35000, rack: 'A-01-02' },
            { code: 'MAT-1002', name: 'SMD 정밀 가공 칩셋 B', category: '전자부품', stock: 85, safeStock: 150, unitPrice: 12000, rack: 'B-04-11' },
            { code: 'MAT-1003', name: '친환경 완충 포장 패키지', category: '포장재', stock: 1200, safeStock: 500, unitPrice: 2500, rack: 'C-02-01' },
            { code: 'MAT-1004', name: '산업용 고온 내열 접착제 5L', category: '부자재', stock: 24, safeStock: 50, unitPrice: 48000, rack: 'D-01-05' },
            { code: 'MAT-1005', name: '스테인리스 스크류 M4 (1000ea)', category: '부자재', stock: 320, safeStock: 100, unitPrice: 8500, rack: 'D-02-09' },
            { code: 'MAT-1006', name: '메인 컨트롤러 PCB 모듈', category: '전자부품', stock: 18, safeStock: 40, unitPrice: 125000, rack: 'B-01-03' }
        ];

        // Inbound / Outbound History Logs State
        let inboundHistory = [
            { id: 'IN-20260729-01', time: '2026-07-29 09:15', code: 'MAT-1001', name: '고강도 알루미늄 프레임 A', qty: 150, vendor: '(주)한성금속', location: 'A-01-02', status: 'SAP MIGO 완료' },
            { id: 'IN-20260728-04', time: '2026-07-28 14:30', code: 'MAT-1003', name: '친환경 완충 포장 패키지', qty: 500, vendor: '그린팩공업', location: 'C-02-01', status: 'SAP MIGO 완료' }
        ];

        let outboundHistory = [
            { id: 'OUT-20260729-02', time: '2026-07-29 11:40', code: 'MAT-1002', name: 'SMD 정밀 가공 칩셋 B', qty: 30, dept: '생산1팀 (Line-A)', requester: '박민수 과장', status: 'SAP GI 계상완료' },
            { id: 'OUT-20260729-01', time: '2026-07-29 08:50', code: 'MAT-1004', name: '산업용 고온 내열 접착제 5L', qty: 5, dept: '품질보증팀', requester: '최지혜 대리', status: 'SAP GI 계상완료' }
        ];

        // Realtime ERP Interface Log Buffer
        let erpLogs = [
            { time: new Date().toLocaleTimeString(), type: 'SUCCESS', text: '[SAP Interface] REST API connection verified. Latency: 12ms' },
            { time: new Date(Date.now() - 300000).toLocaleTimeString(), type: 'SUCCESS', text: '[MIGO] Goods Receipt IN-20260729-01 posted to SAP MM module (Mat: MAT-1001, Qty: 150)' },
            { time: new Date(Date.now() - 600000).toLocaleTimeString(), type: 'INFO', text: '[ERP Sync] Inventory batch status updated for 6 active items' }
        ];

        let pendingTransactions = 0;
        let trendChartInstance = null;
        let categoryChartInstance = null;

        // Initialize App
        document.addEventListener('DOMContentLoaded', () => {
            initCharts();
            renderAll();
            populateSelectOptions();
        });

        // Tab Switch Logic
        function switchTab(tabName) {
            const tabs = ['dashboard', 'inbound', 'outbound', 'inventory', 'logs'];
            const titles = {
                dashboard: { title: 'ERP 연동 자재 관리 종합 대시보드', desc: '실시간 자재 수급 상태 및 ERP 자동 전송 트랜잭션을 한눈에 확인합니다.' },
                inbound: { title: '자재 입고 등록 및 수급 관리', desc: '실체 입고 데이터를 등록하고 ERP Material Management 시스템에 즉시 동기화합니다.' },
                outbound: { title: '자재 불출 및 생산 출고 관리', desc: '현장 불출 요청을 처리하고 SAP ERP의 CO/GI 비용 계정에 자동 전송합니다.' },
                inventory: { title: '실시간 통합 자재 재고 현황', desc: '현장 실물 수량과 ERP 장부 수량이 자동 동기화되는 통합 자재 목록입니다.' },
                logs: { title: 'ERP 인터페이스 실시간 송수신 로그', desc: 'WMS/MES/SAP 연동 시스템의 API 호출 및 데이터 가공 로그 내역입니다.' }
            };

            tabs.forEach(t => {
                const el = document.getElementById(`tab-content-${t}`);
                const nav = document.getElementById(`nav-${t}`);
                if (t === tabName) {
                    el.classList.remove('hidden');
                    nav.classList.add('bg-blue-600', 'text-white', 'shadow-md');
                    nav.classList.remove('hover:bg-slate-800', 'text-slate-400');
                } else {
                    el.classList.add('hidden');
                    nav.classList.remove('bg-blue-600', 'text-white', 'shadow-md');
                    nav.classList.add('hover:bg-slate-800', 'text-slate-400');
                }
            });

            document.getElementById('pageTitle').innerText = titles[tabName].title;
            document.getElementById('pageDescription').innerText = titles[tabName].desc;
        }

        // Main Render Controller
        function renderAll() {
            renderKPIs();
            renderDashboardLowStock();
            renderDashboardLogsStream();
            renderInboundTable();
            renderOutboundTable();
            renderInventoryTable();
            renderFullLogs();
            updateCharts();
        }

        // Render KPI Section
        function renderKPIs() {
            document.getElementById('kpi-total-items').innerText = `${materials.length} 품목`;

            const todayInboundCount = inboundHistory.length;
            const totalInboundQty = inboundHistory.reduce((sum, h) => sum + h.qty, 0);
            document.getElementById('kpi-inbound-today').innerText = `${todayInboundCount} 건`;
            document.getElementById('kpi-inbound-amount').innerText = `누적 수량: ${totalInboundQty.toLocaleString()} 개`;

            const todayOutboundCount = outboundHistory.length;
            const totalOutboundQty = outboundHistory.reduce((sum, h) => sum + h.qty, 0);
            document.getElementById('kpi-outbound-today').innerText = `${todayOutboundCount} 건`;
            document.getElementById('kpi-outbound-amount').innerText = `누적 수량: ${totalOutboundQty.toLocaleString()} 개`;

            const lowStockItems = materials.filter(m => m.stock < m.safeStock);
            document.getElementById('kpi-low-stock').innerText = `${lowStockItems.length} 품목`;
        }

        // Render Dashboard Urgent Alert Table
        function renderDashboardLowStock() {
            const tbody = document.getElementById('dashboardLowStockBody');
            const lowStockItems = materials.filter(m => m.stock < m.safeStock);

            if (lowStockItems.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400">안전재고 미달 품목이 없습니다. (양호)</td></tr>`;
                return;
            }

            tbody.innerHTML = lowStockItems.map(m => `
                <tr class="hover:bg-rose-50/50 transition-colors">
                    <td class="p-2.5 font-mono font-bold text-slate-700">${m.code}</td>
                    <td class="p-2.5 font-medium text-slate-800">${m.name}</td>
                    <td class="p-2.5 text-right font-bold text-rose-600">${m.stock.toLocaleString()}</td>
                    <td class="p-2.5 text-right text-slate-500">${m.safeStock.toLocaleString()}</td>
                    <td class="p-2.5 text-center">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700">부족 (${m.safeStock - m.stock}개)</span>
                    </td>
                </tr>
            `).join('');
        }

        // Render Log Stream on Dashboard
        function renderDashboardLogsStream() {
            const stream = document.getElementById('dashboardLogsStream');
            stream.innerHTML = erpLogs.slice(0, 5).map(l => `
                <div class="p-2.5 rounded-lg border border-slate-100 bg-slate-50 flex items-start justify-between gap-2">
                    <div class="space-y-0.5">
                        <span class="inline-block px-1.5 py-0.2 text-[9px] font-bold rounded ${l.type === 'SUCCESS' ? 'bg-emerald-100 text-emerald-700' : l.type === 'AUTO_PO' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'}">${l.type}</span>
                        <p class="text-slate-700 font-sans leading-snug">${l.text}</p>
                    </div>
                    <span class="text-[10px] text-slate-400 font-mono whitespace-nowrap">${l.time}</span>
                </div>
            `).join('');
        }

        // Render Inbound Table
        function renderInboundTable() {
            const tbody = document.getElementById('inboundTableBody');
            tbody.innerHTML = inboundHistory.map(h => `
                <tr class="hover:bg-slate-50">
                    <td class="p-3 font-mono text-slate-600">${h.id}</td>
                    <td class="p-3 text-slate-500">${h.time}</td>
                    <td class="p-3 font-medium text-slate-900"><span class="font-mono text-blue-600 font-bold">[${h.code}]</span> ${h.name}</td>
                    <td class="p-3 text-right font-bold text-emerald-600">+${h.qty.toLocaleString()}</td>
                    <td class="p-3 text-slate-600">${h.vendor}</td>
                    <td class="p-3 font-mono text-slate-500">${h.location}</td>
                    <td class="p-3 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            <i class="fa-solid fa-check mr-1"></i> ${h.status}
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        // Render Outbound Table
        function renderOutboundTable() {
            const tbody = document.getElementById('outboundTableBody');
            tbody.innerHTML = outboundHistory.map(h => `
                <tr class="hover:bg-slate-50">
                    <td class="p-3 font-mono text-slate-600">${h.id}</td>
                    <td class="p-3 text-slate-500">${h.time}</td>
                    <td class="p-3 font-medium text-slate-900"><span class="font-mono text-indigo-600 font-bold">[${h.code}]</span> ${h.name}</td>
                    <td class="p-3 text-right font-bold text-indigo-600">-${h.qty.toLocaleString()}</td>
                    <td class="p-3 text-slate-600">${h.dept}</td>
                    <td class="p-3 text-slate-600">${h.requester}</td>
                    <td class="p-3 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 text-indigo-800">
                            <i class="fa-solid fa-check mr-1"></i> ${h.status}
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        // Render Master Realtime Inventory Table
        function renderInventoryTable() {
            const category = document.getElementById('categoryFilter').value;
            const status = document.getElementById('stockStatusFilter').value;
            const search = document.getElementById('inventorySearch').value.toLowerCase();

            const tbody = document.getElementById('inventoryTableBody');

            let filtered = materials.filter(m => {
                const matchCategory = (category === 'ALL' || m.category === category);
                const matchStatus = (status === 'ALL' || (status === 'LOW' ? m.stock < m.safeStock : m.stock >= m.safeStock));
                const matchSearch = (m.name.toLowerCase().includes(search) || m.code.toLowerCase().includes(search));
                return matchCategory && matchStatus && matchSearch;
            });

            tbody.innerHTML = filtered.map(m => {
                const isLow = m.stock < m.safeStock;
                const totalAssetValue = m.stock * m.unitPrice;
                return `
                    <tr class="hover:bg-slate-50">
                        <td class="p-3 font-mono font-bold text-blue-600">${m.code}</td>
                        <td class="p-3 font-medium text-slate-900">${m.name}</td>
                        <td class="p-3 text-slate-500">${m.category}</td>
                        <td class="p-3 text-right font-bold ${isLow ? 'text-rose-600 font-black' : 'text-slate-800'}">${m.stock.toLocaleString()}</td>
                        <td class="p-3 text-right text-slate-500">${m.safeStock.toLocaleString()}</td>
                        <td class="p-3 text-right text-slate-600 font-mono">${m.unitPrice.toLocaleString()}</td>
                        <td class="p-3 text-right font-semibold text-slate-800 font-mono">${totalAssetValue.toLocaleString()}</td>
                        <td class="p-3 font-mono text-slate-500">${m.rack}</td>
                        <td class="p-3 text-center">
                            ${isLow ? 
                                `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700 animate-pulse">부족</span>` : 
                                `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700">정상</span>`}
                        </td>
                        <td class="p-3 text-center">
                            <button onclick="triggerManualPo('${m.code}')" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-white rounded text-[10px] font-medium transition-colors">
                                발주요청
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // Full ERP Logs View
        function renderFullLogs() {
            const container = document.getElementById('fullLogContainer');
            container.innerHTML = erpLogs.map(l => `
                <div class="flex items-start gap-3 border-b border-slate-800/80 pb-1.5">
                    <span class="text-slate-500 whitespace-nowrap">${l.time}</span>
                    <span class="font-bold ${l.type === 'SUCCESS' ? 'text-emerald-400' : l.type === 'AUTO_PO' ? 'text-amber-400' : 'text-blue-400'}">[${l.type}]</span>
                    <span class="text-slate-300 flex-1">${l.text}</span>
                </div>
            `).join('');
        }

        // Modal Handlers
        function openInboundModal() {
            document.getElementById('inboundModal').classList.remove('hidden');
            document.getElementById('inboundModal').classList.add('flex');
        }
        function closeInboundModal() {
            document.getElementById('inboundModal').classList.add('hidden');
            document.getElementById('inboundModal').classList.remove('flex');
        }
        function openOutboundModal() {
            document.getElementById('outboundModal').classList.remove('hidden');
            document.getElementById('outboundModal').classList.add('flex');
        }
        function closeOutboundModal() {
            document.getElementById('outboundModal').classList.add('hidden');
            document.getElementById('outboundModal').classList.remove('flex');
        }

        function populateSelectOptions() {
            const inboundSelect = document.getElementById('inboundMaterialCode');
            const outboundSelect = document.getElementById('outboundMaterialCode');

            const options = materials.map(m => `<option value="${m.code}">[${m.code}] ${m.name} (현재: ${m.stock}개)</option>`).join('');
            inboundSelect.innerHTML = options;
            outboundSelect.innerHTML = options;
        }

        // Action Handlers
        function handleInboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById('inboundMaterialCode').value;
            const qty = parseInt(document.getElementById('inboundQty').value);
            const vendor = document.getElementById('inboundVendor').value;
            const location = document.getElementById('inboundLocation').value || 'A-Zone';

            const mat = materials.find(m => m.code === code);
            if (mat) {
                mat.stock += qty;
                const newId = `IN-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${String(inboundHistory.length + 1).padStart(2, '0')}`;
                
                inboundHistory.unshift({
                    id: newId,
                    time: new Date().toISOString().slice(0, 16).replace('T', ' '),
                    code: mat.code,
                    name: mat.name,
                    qty: qty,
                    vendor: vendor,
                    location: location,
                    status: 'SAP MIGO 완료'
                });

                addLog('SUCCESS', `[SAP MIGO] Direct Inbound completed. Material: ${mat.code}, Qty: +${qty}, Doc: ${newId}`);
                closeInboundModal();
                renderAll();
                populateSelectOptions();
                document.getElementById('inboundForm').reset();
            }
        }

        function handleOutboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById('outboundMaterialCode').value;
            const qty = parseInt(document.getElementById('outboundQty').value);
            const dept = document.getElementById('outboundDept').value;
            const requester = document.getElementById('outboundRequester').value;

            const mat = materials.find(m => m.code === code);
            if (mat) {
                if (mat.stock < qty) {
                    alert(`출고 불가: 현재 재고(${mat.stock}개)보다 요청 수량(${qty}개)이 많습니다.`);
                    return;
                }

                mat.stock -= qty;
                const newId = `OUT-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${String(outboundHistory.length + 1).padStart(2, '0')}`;

                outboundHistory.unshift({
                    id: newId,
                    time: new Date().toISOString().slice(0, 16).replace('T', ' '),
                    code: mat.code,
                    name: mat.name,
                    qty: qty,
                    dept: dept,
                    requester: requester,
                    status: 'SAP GI 계상완료'
                });

                addLog('SUCCESS', `[SAP Goods Issue] Outbound approved. CostCenter mapped. Material: ${mat.code}, Qty: -${qty}, Doc: ${newId}`);
                closeOutboundModal();
                renderAll();
                populateSelectOptions();
                document.getElementById('outboundForm').reset();
            }
        }

        // ERP Auto Purchase Order Simulation
        function simulateErpAutoOrder() {
            const lowItems = materials.filter(m => m.stock < m.safeStock);
            if (lowItems.length === 0) {
                alert('현재 안전재고 미달 품목이 없어 ERP 발주 생성이 필요하지 않습니다.');
                return;
            }

            lowItems.forEach(m => {
                const poQty = (m.safeStock * 2) - m.stock;
                addLog('AUTO_PO', `[ERP Auto PO Generated] PR/PO auto-created in SAP MM for ${m.code} (${m.name}). Target Order Qty: ${poQty} EA`);
            });

            alert(`ERP 자동 발주 시뮬레이션 완료:\n${lowItems.length}개 부족 품목에 대한 SAP 구매요청(PR) 및 발주서(PO) 생성이 수신 로그에 등록되었습니다.`);
            renderAll();
        }

        function triggerManualPo(code) {
            const mat = materials.find(m => m.code === code);
            if (mat) {
                addLog('AUTO_PO', `[Manual PO Trigger] User created manual SAP Purchase Requisition for ${mat.code}`);
                alert(`[${mat.code}] ${mat.name} 항목의 ERP 수동 발주 요청이 전송되었습니다.`);
                renderAll();
            }
        }

        function triggerErpSync() {
            const icon = document.getElementById('syncIcon');
            icon.classList.add('fa-spin');
            
            setTimeout(() => {
                icon.classList.remove('fa-spin');
                document.getElementById('lastSyncTime').innerText = '방금 전';
                addLog('INFO', '[SAP RFC] Manual real-time master data synchronization completed with 0 errors.');
                renderAll();
            }, 800);
        }

        function addLog(type, text) {
            erpLogs.unshift({
                time: new Date().toLocaleTimeString(),
                type: type,
                text: text
            });
        }

        function clearLogs() {
            erpLogs = [];
            renderAll();
        }

        // Filters for Tables
        function filterInboundTable() {
            const val = document.getElementById('inboundSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#inboundTableBody tr');
            rows.forEach(r => {
                r.style.display = r.innerText.toLowerCase().includes(val) ? '' : 'none';
            });
        }

        function filterOutboundTable() {
            const val = document.getElementById('outboundSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#outboundTableBody tr');
            rows.forEach(r => {
                r.style.display = r.innerText.toLowerCase().includes(val) ? '' : 'none';
            });
        }

        // Initialize Chart.js Visualization
        function initCharts() {
            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            trendChartInstance = new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: ['7일 전', '6일 전', '5일 전', '4일 전', '3일 전', '어제', '오늘'],
                    datasets: [
                        {
                            label: '입고 수량 (EA)',
                            data: [320, 450, 200, 600, 400, 550, 650],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.08)',
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2
                        },
                        {
                            label: '출고 수량 (EA)',
                            data: [280, 390, 310, 480, 520, 410, 350],
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
                        x: { grid: { display: false } },
                        y: { border: { dash: [4, 4] } }
                    }
                }
            });

            const ctxCategory = document.getElementById('categoryChart').getContext('2d');
            categoryChartInstance = new Chart(ctxCategory, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { font: { family: 'Pretendard', size: 11 }, boxWidth: 12 } }
                    },
                    cutout: '70%'
                }
            });
        }

        function updateCharts() {
            if (!categoryChartInstance) return;

            // Group total valuation by category
            const categorySums = {};
            materials.forEach(m => {
                const val = m.stock * m.unitPrice;
                categorySums[m.category] = (categorySums[m.category] || 0) + val;
            });

            categoryChartInstance.data.labels = Object.keys(categorySums);
            categoryChartInstance.data.datasets[0].data = Object.values(categorySums);
            categoryChartInstance.update();
        }
    </script>
</body>
</html>
