# -*- coding: utf-8 -*-
import io
p = 'build_ct_update_pdf_v2.py'
s = io.open(p, encoding='utf-8').read()
a = s.index('para("Part 1 &mdash;')
b = s.index('# ================================================================ PART 2')
Q = '\\"'
new = '''para("Part 1 &mdash; Point the seven trigger links at the real checkouts (20 min)", "H1")

para("Why this part has to be done, and done first", "H2")
para("A trigger link is a tracked address that GHL owns. When a client clicks it, GHL records the click on that client's record and then "
     "forwards them to the real page. The Enroll buttons in the continuation emails are trigger links for exactly that reason: the click is "
     "the signal that a graduate looked at an offer.")
steps([
    "<b>The click is what starts WF-CT2.</b> WF-CT2 Continuation Engagement listens for clicks on the seven Enroll links. A click adds the tag "
    + C("continuation-engaged") + " and moves the client's card to Call Booked / Reply Received. Without the trigger links, GHL never knows "
    "the client was interested.",
    "<b>The 5-day follow-up depends on it.</b> Five days after the outreach email, the workflow checks for " + C("continuation-engaged")
    + ". If the click was never recorded, an interested client is filed as no response and Luann gets a follow-up task she does not need.",
    "<b>The links exist but go nowhere.</b> All seven were created during the build with placeholders such as " + C("Enroll-RFB-6mo.com")
    + " because the checkout pages were not confirmed yet. Today a click would record an engagement and then land the client on a dead address.",
    "<b>Seven links, not five,</b> even though RFB and Forge share a checkout. Keeping RFB and Forge as separate names means a click tells you "
    "which gender's email the client opened, which is the only attribution the emails have.",
    "<b>Standard link, not installments.</b> The Standard page carries pay in full, split pay, PayPal and buy now pay later on one screen. "
    "The installments page is a separate ThriveCart product for ThrivePay plans only. One button, one page, fewest decisions for the client.",
])
para("How it flows once the links are right", "XBody")
block([
    "Client clicks an Enroll button in the email",
    "        |",
    "        v",
    "link.fgfunnels.com/...   <- the trigger link. GHL records the click,",
    "        |                   adds continuation-engaged, moves the card    (WF-CT2)",
    "        v",
    "sophieorozco.thrivecart.com/...   <- the checkout. The client pays here.",
])

para("The exact links, copied character for character from Chris's doc", "H2")
para("Use the <b>Standard</b> link for the button. The installments link is listed under each one only for the case where Chris wants it as a "
     "second button.")
block([
    "ENROLL-RFB-6mo  and  ENROLL-Forge-6mo                                   $4,997",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/rfb-forge-6-months-standard-link/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/rfb-forge-6months-installments/",
])
block([
    "ENROLL-RFB-1yr  and  ENROLL-Forge-1yr                                   $8,500",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/rfb-forge-1year-standardlink/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/rfb-forge-1-year-installments/",
])
block([
    "ENROLL-RMMPlus   (RMM Continuation with Coaching, 4 x 1:1 calls)        $2,997",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/rmm-continuation-plus-coaching-2997-standard-link/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/rmm-continuation-coaching-2997-installments/",
])
block([
    "ENROLL-ContinueRMM-6mo   (RMM Continuation, 6 months, no coaching)      $2,000",
    "Standard link, use this for the button:",
    "https://sophieorozco.thrivecart.com/2000-rmm-continuation-standard-link/",
    "ThriveCart installments link, only if a second button is wanted:",
    "https://sophieorozco.thrivecart.com/2000-rmm-continuation-installments/",
])
block([
    "ENROLL-ContinueRMM-3mo   (RMM Continuation, 3 months, no coaching)      $1,500",
    "Listed in the doc under QThrive Cart Installments LinkQ:",
    "https://sophieorozco.thrivecart.com/1500-rmm-continuation-3-months-standard-link/",
    "Listed in the doc under QStandard Link w/ split pay and paypal and BNPLQ:",
    "https://sophieorozco.thrivecart.com/1500-rmm-continuation-installments/",
    "The two labels look swapped. Confirm with Chris which is which before pasting.",
])

para("Set up, one link at a time", "H2")
steps([
    "In the left menu click <b>Marketing</b>. Along the top of the Marketing page click the <b>Trigger Links</b> tab. A table lists every "
    "trigger link in the account by name, with its current destination in the Link URL column.",
    "Find the row named " + C("Enroll-RFB-6mo") + ". On the right of that row click the <b>pencil</b> icon. An edit panel opens with two fields: "
    "<b>Name</b> and <b>Link URL</b>.",
    "Do not touch <b>Name</b>. The WF-CT2 trigger and the email buttons find the link by this name, so it must stay exactly as it is.",
    "Click into <b>Link URL</b>. Select everything in it and delete it. The placeholder " + C("Enroll-RFB-6mo.com") + " must be gone completely.",
    "Paste the Standard link for that program from the block above. For " + C("Enroll-RFB-6mo") + " that is "
    + C("https://sophieorozco.thrivecart.com/rfb-forge-6-months-standard-link/") + ". Paste it, do not type it. Check there is no space at "
    "either end and that it starts with https.",
    "Click <b>Save</b>. The row now shows the ThriveCart address in the Link URL column.",
    "Test that one link before doing the rest. On the same row click the <b>copy</b> icon to copy the trigger link's own address, the one on "
    "link.fgfunnels.com. Open a private browser window, paste it, press Enter. It must land on the ThriveCart page showing $4,997. If it lands "
    "anywhere else, the pasted address is wrong: reopen the row and paste again.",
    "Repeat steps 2 to 7 for the remaining six rows, working down the checklist below.",
])
table(["Trigger link name", "Paste the Standard link ending in", "Page should show"], [
    ["Enroll-RFB-6mo", "rfb-forge-6-months-standard-link/", "$4,997"],
    ["Enroll-Forge-6mo", "rfb-forge-6-months-standard-link/", "$4,997"],
    ["Enroll-RFB-1yr", "rfb-forge-1year-standardlink/", "$8,500"],
    ["Enroll-Forge-1yr", "rfb-forge-1year-standardlink/", "$8,500"],
    ["Enroll-RMMPlus", "rmm-continuation-plus-coaching-2997-standard-link/", "$2,997"],
    ["Enroll-ContinueRMM-6mo", "2000-rmm-continuation-standard-link/", "$2,000"],
    ["Enroll-ContinueRMM-3mo", "1500-rmm-continuation-3-months-standard-link/ once Chris confirms", "$1,500"],
], [1.9*inch, 4.1*inch, 1.3*inch], mono_cols=(0,1))
verify("all seven rows in the Trigger Links table show a sophieorozco.thrivecart.com address, none still ends in .com alone, and each "
       "tested link lands on the ThriveCart page with the price in the checklist. Do not start Part 2 until this is true, because the email "
       "buttons in Part 2 point at these same seven links.")
warn("<b>Two things to confirm with Chris before pasting the last one.</b> In his doc the two labels on the 3-month links are reversed: the "
     "QinstallmentsQ label sits on the slug that ends in standard-link. The checklist goes by the slug. And whether the ThrivePay "
     "installments page should be a second button. If yes, add seven more trigger links named the same with an " + C("-Installments")
     + " suffix, pointing at the installments addresses in the blocks above, and add all seven to the click trigger in WF-CT2 in Part 5.")

'''.replace('Q', Q)
s = s[:a] + new + s[b:]
io.open(p, 'w', encoding='utf-8').write(s)
print('Part 1 expanded; Q placeholders replaced:', 'QThrive' not in s)
