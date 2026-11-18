from bpmn import Model

def receive_and_check():
    m = Model("Receive and check order", "Receive_and_check_order",
              ["Order Desk Clerk", "Sales Representative"],
              doc="L3 as-is, Düsseldorf workshop Week 3 (Table 4.3). Owner: O2C Process Owner. Level: L3. S/4HANA wave: Wave 1.")
    m.n("s", "start", "Customer purchase order received", "Order Desk Clerk", 0)
    m.n("t1", "task", "Receive purchase order", "Order Desk Clerk", 1, doc="IT system: Outlook. Pain point: 40% of orders arrive as PDF by e-mail.")
    m.n("t2", "task", "Check price against PriceBook", "Order Desk Clerk", 2, doc="IT system: PriceBook. Pain point: price differs on about 1 order in 5.")
    m.n("g1", "xor", "Price matches PriceBook?", "Order Desk Clerk", 3)
    m.n("t3", "task", "Clarify price with Sales", "Sales Representative", 4, doc="IT systems: Outlook, Salesforce. Output: confirmed price. Pain point: waiting time 1-3 days.")
    m.n("g2", "xor", "", "Order Desk Clerk", 5)
    m.n("t4", "task", "Check configuration", "Order Desk Clerk", 6, doc="IT system: SAP ECC.")
    m.n("t5", "task", "Create sales order", "Order Desk Clerk", 7, doc="IT system: SAP ECC (VA01). Pain point: manual entry, about 12 minutes per order.")
    m.n("t6", "task", "Send order confirmation", "Order Desk Clerk", 8, doc="IT system: SAP ECC (output BA00). Pain point: sent before the credit check.")
    m.n("e", "end", "Order confirmed", "Order Desk Clerk", 9)
    for a, b in [("s", "t1"), ("t1", "t2"), ("t2", "g1")]: m.f(a, b)
    m.f("g1", "g2", "yes"); m.f("g1", "t3", "no"); m.f("t3", "g2")
    for a, b in [("g2", "t4"), ("t4", "t5"), ("t5", "t6"), ("t6", "e")]: m.f(a, b)
    return m

def manage_credit():
    m = Model("Manage credit", "Manage_credit", ["SAP ECC", "Order Desk Clerk", "Credit Analyst (Pune GCC)"],
              doc="L3 as-is. Called from the L2 overview. End events: Credit released, Order rejected.")
    m.n("s", "start", "Sales order created", "SAP ECC", 0)
    m.n("c1", "call", "Check customer credit", "SAP ECC", 1, called="Check_customer_credit", doc="Automatic credit check in SAP ECC (credit management FD32 / VKM1).")
    m.n("g1", "xor", "Credit block set?", "SAP ECC", 2)
    m.n("gj", "xor", "", "SAP ECC", 6)
    m.n("e1", "end", "Credit released", "SAP ECC", 7)
    m.n("sp", "sub", "Release credit block", "Credit Analyst (Pune GCC)", 3, doc="Site variants: Düsseldorf standard, Brno as-is (S05_Credit_Block_Brno_AsIs.bpmn).")
    m.n("g2", "xor", "Order released?", "Credit Analyst (Pune GCC)", 4)
    m.n("t1", "task", "Inform customer about rejection", "Order Desk Clerk", 5)
    m.n("e2", "end", "Order rejected", "Order Desk Clerk", 6.6)
    m.f("s", "c1"); m.f("c1", "g1"); m.f("g1", "gj", "no"); m.f("gj", "e1"); m.f("g1", "sp", "yes"); m.f("sp", "g2")
    m.f("g2", "gj", "yes"); m.f("g2", "t1", "no"); m.f("t1", "e2")
    return m

def check_customer_credit():
    m = Model("Check customer credit", "Check_customer_credit", ["SAP ECC"], lane_h=220, doc="L3, reusable. Called from Process customer order and Manage credit.")
    m.n("s", "start", "Credit check requested", "SAP ECC", 0)
    m.n("t1", "task", "Determine credit exposure", "SAP ECC", 1)
    m.n("t2", "task", "Compare exposure with credit limit", "SAP ECC", 2)
    m.n("g", "xor", "Within limit?", "SAP ECC", 3)
    m.n("t3", "task", "Set credit block", "SAP ECC", 4, dy=40)
    m.n("e1", "end", "Credit OK", "SAP ECC", 5, dy=-40)
    m.n("e2", "end", "Order blocked for credit", "SAP ECC", 5, dy=40)
    m.f("s", "t1"); m.f("t1", "t2"); m.f("t2", "g"); m.f("g", "e1", "yes"); m.f("g", "t3", "no"); m.f("t3", "e2")
    return m

def deliver_goods():
    m = Model("Deliver goods", "Deliver_goods", ["Logistics", "SAP ECC"], doc="L3 as-is. Activities as in the event log: Create delivery, Pick goods, Post goods issue.")
    m.n("s", "start", "Order released for delivery", "Logistics", 0)
    m.n("t1", "task", "Create delivery", "Logistics", 1, doc="SAP ECC VL01N. One order can have several deliveries (partial deliveries).")
    m.n("t2", "task", "Pick goods", "Logistics", 2, doc="Warehouse transfer order (LTAK).")
    m.n("t3", "task", "Pack and load", "Logistics", 3)
    m.n("t4", "task", "Post goods issue", "SAP ECC", 4, doc="Material document, movement type 601.")
    m.n("t5", "task", "Hand over to carrier", "Logistics", 5)
    m.n("e", "end", "Goods shipped", "Logistics", 6)
    for a, b in [("s", "t1"), ("t1", "t2"), ("t2", "t3"), ("t3", "t4"), ("t4", "t5"), ("t5", "e")]: m.f(a, b)
    return m

def bill_customer():
    m = Model("Bill customer", "Bill_customer", ["Billing", "SAP ECC"], lane_h=220,
              doc="L3 as-is with data objects and IT systems (Figure 6.4). 7.8% of invoices are corrected with PriceBook prices.")
    m.n("s", "start", "Proof of delivery received", "Billing", 0)
    m.n("t1", "task", "Create invoice", "SAP ECC", 1, doc="IT system: SAP ECC (VF01, billing type F2).")
    m.n("t2", "task", "Check invoice", "Billing", 2, doc="IT system: PriceBook.")
    m.n("g", "xor", "Price correct?", "Billing", 3)
    m.n("t3", "task", "Correct invoice", "Billing", 4, dy=50, doc="Credit memo (G2) and corrected invoice. IT systems: SAP ECC, PriceBook.")
    m.n("g2", "xor", "", "Billing", 5)
    m.n("t4", "task", "Send invoice", "SAP ECC", 6, doc="Output RD00.")
    m.n("e", "end", "Invoice sent", "SAP ECC", 7)
    m.f("s", "t1"); m.f("t1", "t2"); m.f("t2", "g"); m.f("g", "g2", "yes"); m.f("g", "t3", "no"); m.f("t3", "g2"); m.f("g2", "t4"); m.f("t4", "e")
    m.data("d1", "Delivery [confirmed]", "SAP ECC", 0.15, "t1", "in", dy=-50)
    m.data("d2", "Invoice [created]", "SAP ECC", 1.75, "t1", "out", dy=55)
    m.data("d3", "Invoice [corrected]", "SAP ECC", 3.6, "t3", "out", dy=-45)
    m.data("ds", "PriceBook", "SAP ECC", 4.9, "t3", "in", store=True, dy=-45)
    return m

def manage_receivables():
    m = Model("Manage receivables", "Manage_receivables", ["Accounts Receivable", "SAP ECC"], lane_h=200, doc="L3 as-is. Dunning runs monthly (as-is).")
    m.n("s", "start", "Invoice sent", "Accounts Receivable", 0, dy=-40)
    m.n("gm", "xor", "", "Accounts Receivable", 1, dy=-40)
    m.n("g", "evgw", "", "Accounts Receivable", 1.75, dy=-40)
    m.n("m1", "msgcatch", "Bank statement received", "SAP ECC", 2.6)
    m.n("t1", "task", "Receive incoming payment", "SAP ECC", 3.6)
    m.n("t2", "task", "Clear payment", "Accounts Receivable", 4.6, dy=-40)
    m.n("e", "end", "Payment received", "Accounts Receivable", 5.6, dy=-40)
    m.n("tm", "timer", "Due date passed", "Accounts Receivable", 2.6, dy=50)
    m.n("t3", "task", "Send dunning notice", "Accounts Receivable", 3.6, dy=50, doc="Monthly dunning run (as-is). First reminder on average 18-21 days after the due date.")
    m.external("Bank", above=False); m.msg("P_Bank", "m1", "Bank statement")
    m.f("s", "gm"); m.f("gm", "g"); m.f("g", "m1"); m.f("m1", "t1"); m.f("t1", "t2"); m.f("t2", "e"); m.f("g", "tm"); m.f("tm", "t3"); m.f("t3", "gm", loop=True)
    return m

def overview(collab=False):
    lanes = ["Sales Operations", "Credit Management", "Logistics", "Billing", "Accounts Receivable"]
    name = "Order to Cash - collaboration (L2)" if collab else "Order to Cash - overview (L2)"
    m = Model(name, "O2C_collaboration_L2" if collab else "O2C_overview_L2", lanes,
              doc="L2. Owner: O2C Process Owner. Each collapsed subprocess links to its L3 model.")
    m.n("s", "start", "Customer purchase order received", "Sales Operations", 0)
    m.n("p1", "sub", "Process customer order", "Sales Operations", 1)
    m.n("p2", "sub", "Manage credit", "Credit Management", 2, doc="End events of the L3 model: Credit released, Order rejected.")
    m.n("p3", "sub", "Deliver goods", "Logistics", 3)
    m.n("p4", "sub", "Bill customer", "Billing", 4)
    m.n("p5", "sub", "Manage receivables", "Accounts Receivable", 5)
    m.n("e", "end", "Payment received", "Accounts Receivable", 6)
    for a, b in [("s", "p1"), ("p1", "p2"), ("p2", "p3"), ("p3", "p4"), ("p4", "p5"), ("p5", "e")]: m.f(a, b)
    if collab:
        m.external("Customer", above=True); m.external("Carrier", above=False); m.external("Bank", above=False)
        m.msg("P_Customer", "p1", "Purchase order", -30); m.msg("p1", "P_Customer", "Order confirmation", 30)
        m.msg("p4", "P_Customer", "Invoice", 30)
        m.msg("p3", "P_Carrier", "Transport order", -30); m.msg("P_Carrier", "p3", "Proof of delivery", 30)
        m.msg("P_Bank", "p5", "Bank statement", 30)
    return m

def brno_credit_block():
    L = ["SAP ECC", "Order Desk Clerk (Brno)", "Credit Analyst (Pune GCC)", "Sales Representative"]
    m = Model("Release credit block (Brno) - as-is", "Release_credit_block_Brno_as_is", L, lane_h=280,
              doc="L3 as-is, Brno. Owner: O2C Process Owner. Site applicability: Brno. S/4HANA wave: Wave 1.")
    m.n("s", "start", "Order blocked for credit", "SAP ECC", 0)
    m.n("t1", "task", "Check trusted customer list", "Order Desk Clerk (Brno)", 1, doc="Pain point: list maintained locally in Excel, no owner in finance.")
    m.n("g1", "xor", "Customer on trusted list?", "Order Desk Clerk (Brno)", 2)
    m.n("t2", "task", "Send release request to Pune", "Order Desk Clerk (Brno)", 3, dy=-50)
    m.n("m0", "msgthrow", "Release request sent", "Order Desk Clerk (Brno)", 4, dy=-50)
    m.n("gm", "xor", "", "Order Desk Clerk (Brno)", 5, dy=-50)
    m.n("g2", "evgw", "", "Order Desk Clerk (Brno)", 5.6, dy=-50)
    m.n("m1", "msgcatch", "Release received", "Order Desk Clerk (Brno)", 6.5, dy=-50)
    m.n("tm2", "timer", "48 hours passed", "Order Desk Clerk (Brno)", 6.5, dy=30)
    m.n("t5", "task", "Call credit analyst", "Order Desk Clerk (Brno)", 7.4, dy=30, doc="Pain point: Pune queue sorted by date, not by urgency.")
    m.n("t3", "task", "Review blocked order", "Credit Analyst (Pune GCC)", 8, dy=0)
    m.n("g3", "xor", "Order released?", "Credit Analyst (Pune GCC)", 9, dy=0)
    m.n("t4", "task", "Release credit block", "Credit Analyst (Pune GCC)", 10, dy=0)
    m.n("e1", "end", "Credit block released", "Credit Analyst (Pune GCC)", 11, dy=0)
    m.n("e2", "end", "Order rejected", "Credit Analyst (Pune GCC)", 10.5, dy=-70)
    m.n("tm1", "timer", "2 working days passed", "Order Desk Clerk (Brno)", 3, dy=70, doc="Pain point: average wait 2.6 days.")
    m.n("t6", "task", "Ask Sales to contact customer", "Sales Representative", 4)
    m.n("t7", "task", "Contact customer about payment", "Sales Representative", 5)
    m.n("e3", "end", "Customer contacted", "Sales Representative", 6)
    m.n("t8", "task", "Escalate to Head of Credit", "Credit Analyst (Pune GCC)", 9.3, dy=85)
    m.n("e4", "end", "Escalated", "Credit Analyst (Pune GCC)", 10.3, dy=85)
    m.boundary("b1", "24 hours", "t3")
    m.f("s", "t1"); m.f("t1", "g1"); m.f("g1", "t2", "yes"); m.f("t2", "m0"); m.f("m0", "gm"); m.f("gm", "g2")
    m.f("g2", "m1"); m.f("g2", "tm2"); m.f("m1", "t3"); m.f("tm2", "t5"); m.f("t5", "gm", loop=True)
    m.f("t3", "g3"); m.f("g3", "t4", "yes"); m.f("g3", "e2", "no"); m.f("t4", "e1")
    m.f("g1", "tm1", "no"); m.f("tm1", "t6"); m.f("t6", "t7"); m.f("t7", "e3")
    m.f("b1", "t8"); m.f("t8", "e4")
    return m

def model_approval():
    L = ["Modeller (author)", "Process owner", "Quality reviewer", "Process Governance (system)"]
    m = Model("Velora - Model approval (ISO)", "Velora_Model_approval_ISO", L, lane_h=200,
              doc="Trigger: Process Manager > Signavio approval. Approvers come from the model (Assign using a role: Process owner). "
                  "Reminder after 3 working days; escalation to the L1 process owner after 5 working days (PD-033).")
    S = "Process Governance (system)"
    m.n("s", "start", "Approval requested with reason for change", "Modeller (author)", 0)
    m.n("t1", "task", "Run model guideline check", S, 1)
    m.n("g1", "xor", "Conventions met?", S, 2)
    m.n("t2", "task", "Approve model (process owner)", "Process owner", 3)
    m.n("g2", "xor", "Approved?", "Process owner", 5)
    m.n("g3", "xor", "ISO 9001 relevant?", "Process owner", 6)
    m.n("t3", "task", "Approve model (quality review)", "Quality reviewer", 7)
    m.n("g4", "xor", "Approved?", "Quality reviewer", 8)
    m.n("gj", "xor", "", S, 9)
    m.n("t4", "task", "Set model state to Approved", S, 10, doc="Publish to the Hub; set Next review date to +12 months; request read confirmations.")
    m.n("t5", "task", "E-mail author: approved", S, 11)
    m.n("e1", "end", "Model approved", S, 12)
    m.n("r1", "xor", "", "Modeller (author)", 5)
    m.n("r1b", "xor", "", "Modeller (author)", 8)
    m.n("r2", "task", "E-mail author with comment or error list", "Modeller (author)", 9)
    m.n("r3", "task", "Set model state to rejected", "Modeller (author)", 10)
    m.n("e2", "end", "Model rejected", "Modeller (author)", 11)
    m.boundary("b1", "3 working days", "t2")
    m.n("t6", "task", "Remind; escalate to L1 owner after 5 days", "Process owner", 4, dy=50)
    m.n("e3", "end", "Reminder sent", "Process owner", 5, dy=50)
    m.f("s", "t1"); m.f("t1", "g1"); m.f("g1", "r1", "no"); m.f("g1", "t2", "yes")
    m.f("t2", "g2"); m.f("g2", "g3", "yes"); m.f("g2", "r1", "no")
    m.f("g3", "t3", "yes"); m.f("g3", "gj", "no"); m.f("t3", "g4"); m.f("g4", "gj", "yes"); m.f("g4", "r1b", "no")
    m.f("gj", "t4"); m.f("t4", "t5"); m.f("t5", "e1")
    m.f("r1", "r1b"); m.f("r1b", "r2"); m.f("r2", "r3"); m.f("r3", "e2")
    m.f("b1", "t6"); m.f("t6", "e3")
    return m
