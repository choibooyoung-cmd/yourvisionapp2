import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title="ERP 연동 자재 관리 대시보드",
    page_icon="📦",
    layout="wide"
)

# HTML/CSS/JS 대시보드 코드
html_code = """
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

                <!-- Tables -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                                <tbody id="dashboardLowStockBody" class="divide-y divide-slate-100"></tbody>
                            </table>
                        </div>
                    </div>

                    <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col">
                        <div class="flex items-center justify-between mb-4">
                            <div class="flex items-center gap-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-blue-500 pulse-badge"></span>
                                <h3 class="text-base font-bold text-slate-900">ERP 인터페이스 실시간 동기화 로그</h3>
                            </div>
                            <button onclick="switchTab('logs')" class="text-xs text-blue-600 hover:underline font-semibold">전체 로그 &rarr;</button>
                        </div>
                        <div id="dashboardLogsStream" class="flex-1 space-y-3 overflow-y-auto max-h-56 pr-1 text-xs scrollbar-slim"></div>
                    </div>
                </div>
            </div>

            <!-- 2. TAB: INBOUND -->
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
                            <tbody id="inboundTableBody" class="divide-y divide-slate-100"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 3. TAB: OUTBOUND -->
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
                            <tbody id="outboundTableBody" class="divide-y divide-slate-100"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 4. TAB: INVENTORY -->
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
                            <tbody id="inventoryTableBody" class="divide-y divide-slate-100"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 5. TAB: LOGS -->
            <div id="tab-content-logs" class="hidden space-y-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
                    <div class="flex justify-between items-center mb-4">
                        <div>
                            <h3 class="text-lg font-bold text-slate-900">ERP 인터페이스 송수신 로그 (SAP / MES / WMS)</h3>
                            <p class="text-xs text-slate-500">자재 관리에 따른 자동 API 요청 및 수신 응답 히스토리</p>
                        </div>
                        <button onclick="clearLogs()" class="px-3 py-1.5 text-xs text-slate-500 border border-slate-300 rounded-lg hover:bg-slate-50">로그 초기화</button>
                    </div>

                    <div class="bg-slate-900 text-slate-200 font-mono text-xs p-4 rounded-xl max-h-[550px] overflow-y-auto scrollbar-slim space-y-2 border border-slate-800" id="fullLogContainer"></div>
                </div>
            </div>

        </div>
    </main>

    <!-- Modals -->
    <div id="inboundModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden">
            <div class="px-6 py-4 bg-emerald-600 text-white flex justify-between items-center">
                <h3 class="font-bold text-base flex items-center gap-2"><i class="fa-solid fa-truck-ramp-box"></i> 신규 자재 입고 처리</h3>
                <button onclick="closeInboundModal()" class="text-white/80 hover:text-white text-lg">&times;</button>
            </div>
            <form id="inboundForm" onsubmit="handleInboundSubmit(event)" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">입고 자재 선택</label>
                    <select id="inboundMaterialCode" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 outline-none"></select>
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

    <div id="outboundModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden">
            <div class="px-6 py-4 bg-indigo-600 text-white flex justify-between items-center">
                <h3 class="font-bold text-base flex items-center gap-2"><i class="fa-solid fa-dolly"></i> 신규 자재 출고 불출</h3>
                <button onclick="closeOutboundModal()" class="text-white/80 hover:text-white text-lg">&times;</button>
            </div>
            <form id="outboundForm" onsubmit="handleOutboundSubmit(event)" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">출고 자재 선택</label>
                    <select id="outboundMaterialCode" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none"></select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">출고 수량</label>
                    <input type="number" id="outboundQty" min="1" required placeholder="수량 입력" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">사용 부서 / 프로젝트 코드</label>
                    <input type="text" id="outboundDept" required placeholder="예: 생산1팀 / PRJ-2026-A" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">불출 요청자</label>
                    <input type="text" id="outboundRequester" required placeholder="예: 이생산 대리" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>
                <div class="p-3 bg-indigo-50 rounded-lg border border-indigo-100 text-[11px] text-indigo-800 flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-indigo-600"></i>
                    <span>출고 승인 시 ERP 코스트센터 비용 자산 차감 연동이 실행됩니다.</span>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeOutboundModal()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">취소</button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-md transition-all">출고 승인 및 ERP 계정 매핑</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Application JavaScript Logic -->
    <script>
        const state = {
            materials: [
                { id: "MAT-1001", name: "고강도 알루미늄 프레임 A", category: "원자재", stock: 120, safety: 150, unitPrice: 45000, rack: "A1-Rack-02" },
                { id: "MAT-1002", name: "SMD 파워 인덕터 10uH", category: "전자부품", stock: 8500, safety: 3000, unitPrice: 350, rack: "E2-Rack-05" },
                { id: "MAT-1003", name: "고내열 실리콘 가스켓 B", category: "부자재", stock: 240, safety: 500, unitPrice: 8500, rack: "B3-Rack-01" },
                { id: "MAT-1004", name: "산업용 친환경 방수 포장재", category: "포장재", stock: 1200, safety: 1000, unitPrice: 2100, rack: "P1-Rack-04" },
                { id: "MAT-1005", name: "MCU 메인 컨트롤러 칩셋", category: "전자부품", stock: 85, safety: 200, unitPrice: 32000, rack: "E1-Rack-01" },
                { id: "MAT-1006", name: "스테인리스 볼트 M6x20", category: "부자재", stock: 15000, safety: 5000, unitPrice: 120, rack: "B1-Rack-12" },
                { id: "MAT-1007", name: "강화 아크릴 커버 패널", category: "원자재", stock: 430, safety: 300, unitPrice: 18500, rack: "A2-Rack-08" }
            ],
            inboundLogs: [
                { id: "IN-20260729-01", time: "2026-07-29 09:15", code: "MAT-1002", name: "SMD 파워 인덕터 10uH", qty: 2000, vendor: "(주)한성전자", location: "E2-Rack-05", status: "SAP MIGO 완료" },
                { id: "IN-20260728-04", time: "2026-07-28 14:30", code: "MAT-1006", name: "스테인리스 볼트 M6x20", qty: 5000, vendor: "(주)금성볼트", location: "B1-Rack-12", status: "SAP MIGO 완료" },
                { id: "IN-20260727-02", time: "2026-07-27 11:20", code: "MAT-1001", name: "고강도 알루미늄 프레임 A", qty: 50, vendor: "(주)대한메탈", location: "A1-Rack-02", status: "SAP MIGO 완료" }
            ],
            outboundLogs: [
                { id: "OUT-20260729-01", time: "2026-07-29 10:40", code: "MAT-1003", name: "고내열 실리콘 가스켓 B", qty: 150, dept: "생산2팀 (LINE-B)", requester: "박기술 과장", status: "ERP 비용 처리 완료" },
                { id: "OUT-20260728-02", time: "2026-07-28 16:10", code: "MAT-1005", name: "MCU 메인 컨트롤러 칩셋", qty: 40, dept: "SMT 조립라인", requester: "최조립 대리", status: "ERP 비용 처리 완료" }
            ],
            erpLogs: [
                { time: "15:34:10", level: "INFO", system: "SAP ERP", message: "API [RFC_READ_TABLE] 실행 완료 - 재고 7종 마스터 동기화 100% 정상" },
                { time: "14:20:05", level: "SUCCESS", system: "SAP MIGO", message: "입고 문서 #20260729-01 생성 완료 (Mat: MAT-1002, Qty: +2000)" },
                { time: "11:05:44", level: "WARN", system: "AUTO-PO", message: "경고: 자재 MAT-1005 (MCU 칩셋) 재고(85)가 안전재고(200)에 미달함. 자동 PR 발주 승인 대기중." }
            ]
        };

        let trendChartInstance = null;
        let categoryChartInstance = null;

        document.addEventListener("DOMContentLoaded", () => {
            initDashboard();
            updateSelectOptions();
        });

        function switchTab(tabId) {
            const tabs = ['dashboard', 'inbound', 'outbound', 'inventory', 'logs'];
            const titles = {
                dashboard: { title: "ERP 연동 자재 관리 종합 대시보드", desc: "실시간 자재 수급 상태 및 ERP 자동 전송 트랜잭션을 한눈에 확인합니다." },
                inbound: { title: "자재 입고 관리 및 ERP 전송", desc: "실시간 입고 처리 및 SAP MIGO 입고 문서 자동 동기화 현황입니다." },
                outbound: { title: "자재 출고 불출 및 비용 계정 매핑", desc: "생산 현장 출고 요청 승인 및 코스트센터 계정 자동 매핑 내역입니다." },
                inventory: { title: "실시간 통합 자재 재고 현황", desc: "실물 창고 재고와 ERP 장부 수량 간의 실시간 일치 상태를 관리합니다." },
                logs: { title: "ERP 인터페이스 송수신 로그", desc: "SAP RFC / REST API 모듈 간 실시간 트랜잭션 상세 감시 로그입니다." }
            };

            tabs.forEach(t => {
                const content = document.getElementById(`tab-content-${t}`);
                const navBtn = document.getElementById(`nav-${t}`);
                if (t === tabId) {
                    content.classList.remove('hidden');
                    navBtn.className = "nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all bg-blue-600 text-white shadow-md";
                } else {
                    content.classList.add('hidden');
                    navBtn.className = "nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400";
                }
            });

            document.getElementById('pageTitle').innerText = titles[tabId].title;
            document.getElementById('pageDescription').innerText = titles[tabId].desc;

            if (tabId === 'dashboard') initDashboard();
            else if (tabId === 'inbound') renderInboundTable();
            else if (tabId === 'outbound') renderOutboundTable();
            else if (tabId === 'inventory') renderInventoryTable();
            else if (tabId === 'logs') renderFullLogs();
        }

        function initDashboard() {
            updateKpiCards();
            renderCharts();
            renderDashboardLowStockTable();
            renderDashboardLogsStream();
        }

        function updateKpiCards() {
            document.getElementById('kpi-total-items').innerText = `${state.materials.length} 품목`;

            const todayInbound = state.inboundLogs.filter(x => x.time.includes('2026-07-29'));
            const todayInboundCount = todayInbound.length;
            const todayInboundTotalQty = todayInbound.reduce((acc, curr) => acc + Number(curr.qty), 0);
            document.getElementById('kpi-inbound-today').innerText = `${todayInboundCount} 건`;
            document.getElementById('kpi-inbound-amount').innerText = `금일 수량: ${todayInboundTotalQty.toLocaleString()} 개`;

            const todayOutbound = state.outboundLogs.filter(x => x.time.includes('2026-07-29'));
            const todayOutboundCount = todayOutbound.length;
            const todayOutboundTotalQty = todayOutbound.reduce((acc, curr) => acc + Number(curr.qty), 0);
            document.getElementById('kpi-outbound-today').innerText = `${todayOutboundCount} 건`;
            document.getElementById('kpi-outbound-amount').innerText = `금일 수량: ${todayOutboundTotalQty.toLocaleString()} 개`;

            const lowStockCount = state.materials.filter(m => m.stock < m.safety).length;
            document.getElementById('kpi-low-stock').innerText = `${lowStockCount} 품목`;
        }

        function renderCharts() {
            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            if (trendChartInstance) trendChartInstance.destroy();
            
            trendChartInstance = new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: ['07/23', '07/24', '07/25', '07/26', '07/27', '07/28', '07/29 (오늘)'],
                    datasets: [
                        { label: '입고 수량 (EA)', data: [1200, 800, 1500, 400, 2100, 5000, 2000], borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, tension: 0.3 },
                        { label: '출고 수량 (EA)', data: [900, 1100, 1300, 600, 1800, 2400, 150], borderColor: '#6366f1', backgroundColor: 'rgba(99, 102, 241, 0.1)', fill: true, tension: 0.3 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } },
                    scales: { y: { grid: { color: '#f1f5f9' }, ticks: { font: { size: 10 } } }, x: { grid: { display: false }, ticks: { font: { size: 10 } } } }
                }
            });

            const ctxCategory = document.getElementById('categoryChart').getContext('2d');
            if (categoryChartInstance) categoryChartInstance.destroy();

            const categoryMap = {};
            state.materials.forEach(m => {
                const totalVal = m.stock * m.unitPrice;
                categoryMap[m.category] = (categoryMap[m.category] || 0) + totalVal;
            });

            categoryChartInstance = new Chart(ctxCategory, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(categoryMap),
                    datasets: [{ data: Object.values(categoryMap), backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6'], borderWidth: 2, borderColor: '#ffffff' }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'right', labels: { boxWidth: 10, font: { size: 11 } } } },
                    cutout: '65%'
                }
            });
        }

        function renderDashboardLowStockTable() {
            const tbody = document.getElementById('dashboardLowStockBody');
            const lowItems = state.materials.filter(m => m.stock < m.safety);
            
            if (lowItems.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-slate-400">부족한 안전재고 품목이 없습니다.</td></tr>`;
                return;
            }

            tbody.innerHTML = lowItems.map(m => `
                <tr class="hover:bg-slate-50 transition-colors">
                    <td class="p-2.5 font-mono text-slate-600">${m.id}</td>
                    <td class="p-2.5 font-semibold text-slate-800">${m.name}</td>
                    <td class="p-2.5 text-right font-bold text-rose-600">${m.stock.toLocaleString()}</td>
                    <td class="p-2.5 text-right text-slate-500">${m.safety.toLocaleString()}</td>
                    <td class="p-2.5 text-center">
                        <span class="px-2 py-0.5 bg-rose-100 text-rose-700 rounded-full font-bold text-[10px]">자동발주 대기</span>
                    </td>
                </tr>
            `).join('');
        }

        function renderDashboardLogsStream() {
            const container = document.getElementById('dashboardLogsStream');
            container.innerHTML = state.erpLogs.map(log => {
                let badgeColor = 'bg-slate-100 text-slate-700';
                if (log.level === 'SUCCESS') badgeColor = 'bg-emerald-100 text-emerald-800';
                if (log.level === 'WARN') badgeColor = 'bg-amber-100 text-amber-800';
                if (log.level === 'INFO') badgeColor = 'bg-blue-100 text-blue-800';

                return `
                    <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-100 flex items-start justify-between gap-2">
                        <div class="space-y-0.5">
                            <div class="flex items-center gap-2">
                                <span class="px-1.5 py-0.2 rounded text-[9px] font-bold ${badgeColor}">${log.system}</span>
                                <span class="text-[10px] text-slate-400 font-mono">${log.time}</span>
                            </div>
                            <p class="text-slate-700 font-medium text-[11px]">${log.message}</p>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function renderInboundTable() {
            const tbody = document.getElementById('inboundTableBody');
            tbody.innerHTML = state.inboundLogs.map(log => `
                <tr class="hover:bg-slate-50/80 transition-colors">
                    <td class="p-3 font-mono text-slate-600 font-bold">${log.id}</td>
                    <td class="p-3 text-slate-500 font-mono text-[11px]">${log.time}</td>
                    <td class="p-3">
                        <span class="font-mono text-slate-400 text-[11px] mr-1">[${log.code}]</span>
                        <span class="font-semibold text-slate-800">${log.name}</span>
                    </td>
                    <td class="p-3 text-right font-bold text-emerald-600">+${Number(log.qty).toLocaleString()}</td>
                    <td class="p-3 text-slate-600">${log.vendor}</td>
                    <td class="p-3"><span class="bg-slate-100 px-2 py-0.5 rounded text-slate-600 font-mono">${log.location}</span></td>
                    <td class="p-3 text-center">
                        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-600 border border-emerald-200">
                            <i class="fa-solid fa-check-double mr-1"></i> ${log.status}
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        function renderOutboundTable() {
            const tbody = document.getElementById('outboundTableBody');
            tbody.innerHTML = state.outboundLogs.map(log => `
                <tr class="hover:bg-slate-50/80 transition-colors">
                    <td class="p-3 font-mono text-slate-600 font-bold">${log.id}</td>
                    <td class="p-3 text-slate-500 font-mono text-[11px]">${log.time}</td>
                    <td class="p-3">
                        <span class="font-mono text-slate-400 text-[11px] mr-1">[${log.code}]</span>
                        <span class="font-semibold text-slate-800">${log.name}</span>
                    </td>
                    <td class="p-3 text-right font-bold text-indigo-600">-${Number(log.qty).toLocaleString()}</td>
                    <td class="p-3 text-slate-600 font-medium">${log.dept}</td>
                    <td class="p-3 text-slate-600">${log.requester}</td>
                    <td class="p-3 text-center">
                        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-600 border border-indigo-200">
                            <i class="fa-solid fa-link mr-1"></i> ${log.status}
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        function renderInventoryTable() {
            const tbody = document.getElementById('inventoryTableBody');
            const catFilter = document.getElementById('categoryFilter').value;
            const statusFilter = document.getElementById('stockStatusFilter').value;
            const searchQuery = document.getElementById('inventorySearch').value.toLowerCase();

            const filtered = state.materials.filter(m => {
                const matchesCat = catFilter === 'ALL' || m.category === catFilter;
                const isLow = m.stock < m.safety;
                const matchesStatus = statusFilter === 'ALL' || (statusFilter === 'LOW' && isLow) || (statusFilter === 'NORMAL' && !isLow);
                const matchesSearch = m.name.toLowerCase().includes(searchQuery) || m.id.toLowerCase().includes(searchQuery);

                return matchesCat && matchesStatus && matchesSearch;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="10" class="text-center py-6 text-slate-400">조건에 일치하는 자재가 없습니다.</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(m => {
                const isLow = m.stock < m.safety;
                const totalVal = m.stock * m.unitPrice;

                return `
                    <tr class="hover:bg-slate-50/80 transition-colors">
                        <td class="p-3 font-mono font-bold text-slate-700">${m.id}</td>
                        <td class="p-3 font-semibold text-slate-900">${m.name}</td>
                        <td class="p-3"><span class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[11px]">${m.category}</span></td>
                        <td class="p-3 text-right font-bold ${isLow ? 'text-rose-600' : 'text-slate-800'}">${m.stock.toLocaleString()}</td>
                        <td class="p-3 text-right text-slate-500">${m.safety.toLocaleString()}</td>
                        <td class="p-3 text-right font-mono text-slate-600">${m.unitPrice.toLocaleString()}</td>
                        <td class="p-3 text-right font-mono font-semibold text-slate-800">${totalVal.toLocaleString()}</td>
                        <td class="p-3 font-mono text-slate-500">${m.rack}</td>
                        <td class="p-3 text-center">
                            ${isLow ? 
                                `<span class="px-2 py-0.5 bg-rose-100 text-rose-700 rounded-full text-[10px] font-bold"><i class="fa-solid fa-triangle-exclamation mr-1"></i>재고 부족</span>` : 
                                `<span class="px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full text-[10px] font-bold"><i class="fa-solid fa-circle-check mr-1"></i>정상</span>`
                            }
                        </td>
                        <td class="p-3 text-center">
                            <button onclick="triggerIndividualSync('${m.id}')" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] font-semibold transition-colors">
                                <i class="fa-solid fa-rotate-sharp mr-1"></i>ERP 갱신
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function renderFullLogs() {
            const container = document.getElementById('fullLogContainer');
            container.innerHTML = state.erpLogs.map(log => `
                <div class="border-b border-slate-800/80 pb-2 flex items-start justify-between">
                    <div>
                        <span class="text-slate-500">[${log.time}]</span>
                        <span class="text-blue-400 font-bold ml-1">[${log.system}]</span>
                        <span class="text-slate-300 ml-2">${log.message}</span>
                    </div>
                    <span class="text-[10px] px-1.5 py-0.5 rounded font-bold ${log.level === 'SUCCESS' ? 'bg-emerald-950 text-emerald-400' : log.level === 'WARN' ? 'bg-amber-950 text-amber-400' : 'bg-blue-950 text-blue-400'}">${log.level}</span>
                </div>
            `).join('');
        }

        function updateSelectOptions() {
            const inboundSelect = document.getElementById('inboundMaterialCode');
            const outboundSelect = document.getElementById('outboundMaterialCode');
            const options = state.materials.map(m => `<option value="${m.id}">${m.id} - ${m.name} (현재재고: ${m.stock})</option>`).join('');
            inboundSelect.innerHTML = options;
            outboundSelect.innerHTML = options;
        }

        function openInboundModal() { document.getElementById('inboundModal').classList.remove('hidden'); document.getElementById('inboundModal').classList.add('flex'); }
        function closeInboundModal() { document.getElementById('inboundModal').classList.add('hidden'); document.getElementById('inboundModal').classList.remove('flex'); }
        function openOutboundModal() { document.getElementById('outboundModal').classList.remove('hidden'); document.getElementById('outboundModal').classList.add('flex'); }
        function closeOutboundModal() { document.getElementById('outboundModal').classList.add('hidden'); document.getElementById('outboundModal').classList.remove('flex'); }

        function handleInboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById('inboundMaterialCode').value;
            const qty = Number(document.getElementById('inboundQty').value);
            const vendor = document.getElementById('inboundVendor').value;
            const location = document.getElementById('inboundLocation').value || "일반창고";

            const mat = state.materials.find(m => m.id === code);
            if (mat) mat.stock += qty;

            const now = new Date();
            const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
            const newId = `IN-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(state.inboundLogs.length+1).padStart(2,'0')}`;

            state.inboundLogs.unshift({
                id: newId, time: timeStr, code: code, name: mat ? mat.name : "자재", qty: qty, vendor: vendor, location: location, status: "SAP MIGO 완료"
            });

            state.erpLogs.unshift({
                time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                level: "SUCCESS", system: "SAP MIGO", message: `[신규 입고] ${newId} 처리 - ${mat.name} +${qty} EA (ERP 재고 평가 기장 완료)`
            });

            closeInboundModal();
            updateSelectOptions();
            initDashboard();
            alert("입고 처리가 완료되어 SAP ERP 시스템에 성공적으로 동기화되었습니다.");
        }

        function handleOutboundSubmit(e) {
            e.preventDefault();
            const code = document.getElementById('outboundMaterialCode').value;
            const qty = Number(document.getElementById('outboundQty').value);
            const dept = document.getElementById('outboundDept').value;
            const requester = document.getElementById('outboundRequester').value;

            const mat = state.materials.find(m => m.id === code);
            if (mat) {
                if (mat.stock < qty) {
                    alert(`출고 실패: 현재 재고 수량(${mat.stock})보다 요청 수량(${qty})이 많습니다.`);
                    return;
                }
                mat.stock -= qty;
            }

            const now = new Date();
            const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
            const newId = `OUT-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(state.outboundLogs.length+1).padStart(2,'0')}`;

            state.outboundLogs.unshift({
                id: newId, time: timeStr, code: code, name: mat ? mat.name : "자재", qty: qty, dept: dept, requester: requester, status: "ERP 비용 처리 완료"
            });

            state.erpLogs.unshift({
                time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                level: "SUCCESS", system: "SAP CO", message: `[신규 출고] ${newId} 승인 - ${mat.name} -${qty} EA -> ${dept} 비용 매핑 완료`
            });

            closeOutboundModal();
            updateSelectOptions();
            initDashboard();
            alert("출고 승인이 완료되었으며 코스트센터 계정으로 자동 기장되었습니다.");
        }

        function triggerErpSync() {
            const icon = document.getElementById('syncIcon');
            icon.classList.add('fa-spin');
            
            setTimeout(() => {
                icon.classList.remove('fa-spin');
                const now = new Date();
                const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
                
                document.getElementById('lastSyncTime').innerText = "방금 전";
                state.erpLogs.unshift({
                    time: timeStr, level: "INFO", system: "SAP RFC", message: "수동 실시간 ERP DB 전체 재해시 및 수량 정합성 검증 완료 (오차 0%)"
                });
                
                initDashboard();
                alert("SAP ERP 시스템과의 전체 데이터 실시간 동기화가 완료되었습니다.");
            }, 800);
        }

        function triggerIndividualSync(matId) {
            const now = new Date();
            const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
            state.erpLogs.unshift({
                time: timeStr, level: "INFO", system: "ERP API", message: `단일 자재 [${matId}] ERP 장부 수량과 창고 실물 재고 1:1 검증 및 동기화 완료`
            });
            renderInventoryTable();
            alert(`자재 코드 ${matId}의 ERP 장부 상태가 최신화되었습니다.`);
        }

        function simulateErpAutoOrder() {
            const lowItems = state.materials.filter(m => m.stock < m.safety);
            if (lowItems.length === 0) {
                alert("현재 안전재고 미달 품목이 없어 자동 발주 생성이 필요하지 않습니다.");
                return;
            }

            const now = new Date();
            const timeStr = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;

            lowItems.forEach(item => {
                const reqQty = (item.safety * 2) - item.stock;
                state.erpLogs.unshift({
                    time: timeStr, level: "SUCCESS", system: "ERP MM-PO", message: `[ERP 자동 발주] ${item.name} (${item.id}) - 수량 ${reqQty} EA 구매요청서(PR) 자동 발행 완료`
                });
            });

            initDashboard();
            alert(`안전재고 미달 품목 ${lowItems.length}건에 대해 ERP 구매요청서(PR)가 자동으로 생성되었습니다.`);
        }

        function clearLogs() {
            state.erpLogs = [];
            renderFullLogs();
        }

        function filterInboundTable() {
            const query = document.getElementById('inboundSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#inboundTableBody tr');
            rows.forEach(row => { row.style.display = row.innerText.toLowerCase().includes(query) ? '' : 'none'; });
        }

        function filterOutboundTable() {
            const query = document.getElementById('outboundSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#outboundTableBody tr');
            rows.forEach(row => { row.style.display = row.innerText.toLowerCase().includes(query) ? '' : 'none'; });
        }
    </script>
</body>
</html>
"""

# Streamlit에 HTML 렌더링 (높이 및 스크롤 설정)
components.html(html_code, height=900, scrolling=True)
