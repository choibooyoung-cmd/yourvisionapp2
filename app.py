<div class="p-3 bg-indigo-50 rounded-lg border border-indigo-100 text-[11px] text-indigo-800 flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-indigo-600"></i>
                    <span>출고 승인 시 ERP CO(원가통제) 모듈과 연동되어 원가 배부 처리가 실행됩니다.</span>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" onclick="closeOutboundModal()" class="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg">취소</button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-md transition-all">출고 승인 및 ERP 연동</button>
                </div>
            </form>
        </div>
    </div>

    <!-- JavaScript Application Logic -->
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
            { time: "16:35:10", type: "INFO", module: "SAP-MM", message: "ERP material master synchronization completed successfully. 8 items verified." },
            { time: "16:20:05", type: "SUCCESS", module: "SAP-MIGO", message: "Inbound doc [IN-2026-0729-01] posted to SAP MM inventory ledger." },
            { time: "14:11:50", type: "WARNING", module: "WMS-ALERT", message: "Low stock threshold triggered for [ELE-3001] PLC 메인 제어 마이크로칩 (Stock: 85 < Safety: 100)." },
            { time: "11:20:00", type: "SUCCESS", module: "SAP-CO", message: "Outbound document [OUT-2026-0729-01] cost center allocation processed." }
        ];

        let pendingTxCount = 0;
        let trendChartInstance = null;
        let categoryChartInstance = null;

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
            const tabs = ['dashboard', 'inbound', 'outbound', 'inventory', 'logs'];
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
                dashboard: { title: "ERP 연동 자재 관리 종합 대시보드", desc: "실시간 자재 수급 상태 및 ERP 자동 전송 트랜잭션을 한눈에 확인합니다." },
                inbound: { title: "자재 입고 관리 (Inbound MIGO)", desc: "외부 공급사로부터 입고되는 자재를 검수하고 SAP 재고 장부에 즉시 반영합니다." },
                outbound: { title: "자재 출고 관리 (Outbound Goods Issue)", desc: "생산 현장 불출 요청 승인 및 원가 회계 계정 연동 현황을 관리합니다." },
                inventory: { title: "실시간 자재 재고 현황 (Real-time SCM Inventory)", desc: "창고 위치별 실물 재고와 ERP 장부 재고의 실시간 비교 및 안전재고 모니터링." },
                logs: { title: "ERP 인터페이스 연동 로그 (API / SAP / MES)", desc: "자재 시스템과 외부 ERP 간 실시간 인터페이스 통신 히스토리 및 장애 추적 로그." }
            };
            document.getElementById("pageTitle").innerText = titles[tabName].title;
            document.getElementById("pageDescription").innerText = titles[tabName].desc;
        }

        // --- Render Dashboard Metrics & Tables ---
        function renderDashboard() {
            // KPI Calculations
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
                                <button onclick="triggerAutoOrderFor('${item.code}')" class="px-2 py-1 bg-amber-500 hover:bg-amber-600 text-white rounded text-[10px] font-semibold shadow-xs">ERP 자동발주</button>
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
                                <i class="fa-solid fa-check mr-1"></i> SAP 연동완료
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

        // --- Form Submissions with ERP Simulation ---
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

            inboundHistory.unshift({
                id: newId,
                date: timeStr,
                code: targetMat.code,
                name: targetMat.name,
                qty: qty,
                vendor: vendor,
                location: location,
                erpStatus: "SYNCED"
            });

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

            // Refresh UI
            renderDashboard();
            renderInboundTable();
            renderInventoryTable();
            renderLogs();
            updateCharts();

            showToast(`신규 입고가 등록되고 ERP 장부에 반영되었습니다! (${targetMat.name} +${qty}EA)`);
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

            outboundHistory.unshift({
                id: newId,
                date: timeStr,
                code: targetMat.code,
                name: targetMat.name,
                qty: qty,
                dept: dept,
                requester: requester,
                erpStatus: "SETTLED"
            });

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

            // Refresh UI
            renderDashboard();
            renderOutboundTable();
            renderInventoryTable();
            renderLogs();
            updateCharts();

            showToast(`자재 출고 승인 및 ERP 원가 정산이 완료되었습니다! (${targetMat.name} -${qty}EA)`);
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
                document.getElementById("lastSyncTime").innerText = "방금 전";
                
                const now = new Date();
                logs.unshift({
                    time: `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`,
                    type: "SUCCESS",
                    module: "SAP-RFC",
                    message: "Manual real-time ERP synchronization executed successfully. All inventory ledgers matched."
                });
                renderLogs();
                renderDashboard();
                showToast("SAP ERP와 실시간 동기화가 성공적으로 완료되었습니다!");
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
            // 1. Weekly Trend Line Chart
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

            // 2. Category Donut Chart
            const ctxCat = document.getElementById('categoryChart').getContext('2d');
            
            // Calculate asset amounts by category
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
