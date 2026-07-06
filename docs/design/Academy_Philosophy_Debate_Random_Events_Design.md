# Academy Philosophy Debate Random Events Design

Status: design only. This document does not implement EU5 script, generated data, or localization.

## Scope

These events are for local Academy Philosophy Debate only. They should not fire during historical roundtable nodes, world debate nodes, recess notices, pending result popups, or after the current issue has already been embraced.

Progress direction:

- `+5` or `+10`: pushes the local debate toward accepting the current issue.
- `-5` or `-10`: pushes the local debate toward rejecting the current issue.
- No other progress amount should appear in event options.
- Non-progress costs may use gold, prestige, legitimacy, stability, estate satisfaction, seat stance changes, character modifiers, institution spread, or temporary country modifiers.

Terminology:

- General events: can fire for any current issue.
- Special events: can fire only for the named current issue and should carry issue-specific flavor, cost, or side effect.

## General Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| G01 | The Chair's Summary | The chair condenses three days of argument into a readable brief, and half the room suddenly realizes what the dispute is actually about. | Publish the summary: `+5`, public opinion leans attentive. Redact the dangerous passages: `-5`, court bureaucrats approve. |
| G02 | Crowded Galleries | The galleries fill with students, clerks, idle nobles, and people who swear they only came to hear the shouting. | Keep the doors open: `+5`, public opinion may gain influence. Clear the galleries: `-5`, legitimacy pressure eases. |
| G03 | A Useful Misquotation | A copied line from an authority appears to support the new argument, though the ink is not quite innocent. | Correct it publicly: `+5`, prestige is spent. Let the ambiguity work: `+10`, scholarly community loses trust. |
| G04 | Margins of the Old Book | An old commentary is found in the Academy library and immediately becomes a weapon for both sides. | Treat the old note as evidence: `-5`, clergy or nobles are reassured. Challenge the authority of the note: `+5`, scholarly community gains confidence. |
| G05 | Private Lecture at Dusk | The Chief Scientist offers to spend the evening turning confusion into conviction for a few decisive listeners. | Authorize the lecture: `+10`, the Chief Scientist becomes busier or strained. Save their strength: `-5`, no extra cost. |
| G06 | Minutes for the Ministries | Bureaucrats demand formal minutes before the debate can continue to influence policy. | Give them exact minutes: `-5`, court bureaucrats gain leverage. Keep the argument informal: `+5`, legitimacy is strained. |
| G07 | A Moral Preface | Religious figures ask that the disputed proposition be wrapped in moral caution before anyone calls it wisdom. | Add the preface: `-5`, clergy satisfaction rises. Refuse the preface: `+5`, clergy satisfaction falls. |
| G08 | Merchant Subscription | Burghers offer to fund pamphlets, copied notes, and coffeehouse discussion, provided their names sit near the title. | Accept the subscription: `+5`, burghers gain satisfaction. Reject commercial noise: `-5`, noble approval rises. |
| G09 | Salon Ridicule | A noble salon turns the debate into an evening entertainment and repeats the sharpest jokes by breakfast. | Answer with a formal defense: `+10`, prestige is spent. Let the mockery stand: `-5`, nobles gain satisfaction. |
| G10 | Student Disputation | Students stage their own version of the debate and prove that enthusiasm can be louder than preparation. | Let them argue: `+5`, public opinion stirs. Ban the gathering: `-5`, order is preserved. |
| G11 | Letter from Abroad | A foreign scholar sends a careful letter, which arrives folded like evidence and read like gossip. | Read it aloud: `+5`, a foreign power gains interest. File it quietly: `-5`, diplomatic complications are avoided. |
| G12 | The Missing Manuscript | A missing manuscript arrives from a private collection just as the debate begins to tire. | Publish extracts: `+10`, gold or prestige is spent. Lock it in the archive: `-5`, nobles or clergy approve. |
| G13 | Instrument in the Hall | A working instrument is carried into the debate chamber and placed where theory can no longer pretend to be alone. | Trust the demonstration: `+10`, conservative estates lose satisfaction. Call it preliminary: `-5`, scholars grumble. |
| G14 | A Street Song | The issue escapes the Academy as a song that is half misunderstanding and half recruitment. | Let the song spread: `+5`, public opinion joins the noise. Suppress the song: `-5`, stability pressure eases. |
| G15 | Formal Challenge | A respected opponent challenges the new claim under rules strict enough to make evasion visible. | Back the new argument: `+5`, scholarly community approves. Back the old reading: `-5`, conservative seats gain confidence. |
| G16 | Committee Exhaustion | Everyone knows another month of debate will produce longer speeches, not better reasons. | Force a decision: `+10`, one neutral or opposing group may resent the pressure. Postpone: `-5`, no extra cost. |
| G17 | Translation Quarrel | Two translations of the same key term produce two different futures for the realm. | Sponsor a new translation: `+5`, gold is spent. Keep the traditional wording: `-5`, clergy or nobles approve. |
| G18 | Allegory on Canvas | An artist paints the issue as a scene so flattering to novelty that even its opponents stop to inspect the colors. | Exhibit the work: `+5`, artists gain skill or favor. Keep art out of doctrine: `-5`, clergy approval rises. |
| G19 | Anonymous Denunciation | A sealed accusation claims the debate is a plot, a vanity, or both. The handwriting is conveniently unfamiliar. | Investigate calmly: `+5`, legitimacy is spent. Seize the papers: `-10`, order rises but scholars are chilled. |
| G20 | Consensus After Midnight | By candlelight, tired opponents accidentally admit which points they can no longer deny. | Keep them in session: `+10`, the Chief Scientist or a seated scholar is strained. Adjourn with dignity: `-5`, no extra cost. |

## Meritocracy Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| M01 | Anonymous Examination | The examiners propose removing names from the papers before judgement. Birth complains that ink has become blind. | Adopt anonymous scoring: `+10`, nobles lose satisfaction. Keep names visible: `-5`, nobles approve. |
| M02 | Genealogies on the Table | Great houses bring polished family trees to prove that service is inherited like silver. | Question the trees: `+5`, prestige is spent. Honor hereditary service: `-10`, nobles gain influence. |
| M03 | The Provincial Prodigy | A candidate from a distant province solves a problem that court favorites have avoided for weeks. | Invite them to court: `+10`, local elites resent disruption. Praise them from afar: `-5`, court order remains. |
| M04 | Purchased Office | A lucrative office is quietly offered to a donor's son during the debate. | Expose the sale: `+10`, gold income or noble satisfaction suffers. Accept the arrangement: `-10`, treasury gains comfort. |
| M05 | Merit on the Battlefield | Officers argue that command earned under fire should count more than old names. | Recognize battlefield merit: `+5`, professional military supports reform. Preserve noble command privilege: `-5`, nobles approve. |
| M06 | The Tutor's Nephew | A royal tutor asks for a cabinet post for a brilliant relative whose brilliance is mostly relational. | Demand open assessment: `+5`, court bureaucrats are irritated. Grant the favor: `-5`, legitimacy pressure eases. |
| M07 | Clerical Certificates | Clergy propose that moral certification should precede all public appointment. | Require ability first: `+5`, clergy satisfaction falls. Accept moral certification: `-5`, clergy satisfaction rises. |
| M08 | Guild Tests | City guilds offer practical tests for accountants, engineers, and clerks. | Add practical tests: `+10`, burghers gain satisfaction. Keep classical credentials: `-5`, scholarly conservatives approve. |
| M09 | A Peasant's Petition | A village schoolmaster asks whether talent born under a thatched roof is still talent. | Admit the petition: `+10`, peasants gain satisfaction. Return it to local authorities: `-5`, order is preserved. |
| M10 | Boycott by Old Families | Several noble families threaten to withdraw sons from the Academy if open rankings proceed. | Let them boycott: `+10`, nobles lose satisfaction. Suspend the ranking: `-10`, nobles approve. |
| M11 | Examination Fraud | A leaked answer key reveals that merit can be imitated by money with excellent penmanship. | Purge the examiners: `+5`, stability or prestige is spent. Quietly invalidate only the worst papers: `-5`, scandal is contained. |
| M12 | Public Ranking List | Reformers want the results posted where every family can see what influence did not buy. | Post the rankings: `+10`, nobles and court favorites resent it. Keep rankings private: `-5`, court bureaucrats approve. |
| M13 | Local Language Answers | Provincial candidates ask to answer in local administrative language rather than courtly style. | Permit local answers: `+5`, accepted cultures gain trust. Require court style: `-5`, centralizers approve. |
| M14 | Hereditary Office in Crisis | A hereditary official fails publicly at the exact task the debate claims should be tested. | Use the failure as proof: `+10`, noble satisfaction falls. Shield the office: `-10`, legitimacy is protected. |
| M15 | Scholar Demand for Open Chairs | Academy scholars demand that teaching posts be competed for, not inherited from patrons. | Open the chairs: `+5`, scholarly community gains support. Confirm patron rights: `-5`, patrons are reassured. |
| M16 | Veterans' Service Rolls | Veterans ask whether years of disciplined service count as merit or merely scars. | Count service in appointments: `+5`, professional military approves. Keep civil posts separate: `-5`, bureaucrats approve. |
| M17 | The Crown's Favorite Fails | A favored candidate performs badly in a supervised trial and everyone notices. | Let the result stand: `+10`, legitimacy is strained. Order a second trial: `-10`, court factions approve. |
| M18 | Clean Ink, Dirty Hands | Investigators find that the cleanest exam papers came from the dirtiest patronage network. | Publicly void them: `+10`, prestige is spent. Bury the investigation: `-10`, noble satisfaction rises. |
| M19 | A School Outside the Capital | A provincial school claims it can train officials without court polish. | Recognize the school: `+5`, local autonomy gains confidence. Require capital certification: `-5`, central bureaucrats approve. |
| M20 | Oath of the Examiners | Examiners ask the Crown to protect them from noble retaliation before they publish results. | Swear protection: `+10`, nobles lose satisfaction. Refuse to provoke great houses: `-10`, noble approval rises. |

## Renaissance Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| R01 | A Newly Found Torso | An ancient sculpture is unearthed, and artists insist that stone can argue better than commentaries. | Exhibit it at the Academy: `+10`, clergy unease rises. Store it as a curiosity: `-5`, conservative approval rises. |
| R02 | Anatomy Before the Court | Physicians request a sanctioned anatomical lesson to prove that old diagrams lie politely. | Permit the lesson: `+10`, clergy satisfaction falls. Forbid the spectacle: `-10`, clergy approval rises. |
| R03 | Perspective in the Chapel | A painter's new perspective turns sacred architecture into mathematics. | Celebrate the method: `+5`, artists gain favor. Demand traditional forms: `-5`, clergy satisfaction rises. |
| R04 | Patronage Ledger | Artists reveal that innovation follows patrons more reliably than inspiration follows sermons. | Expand court patronage: `+10`, gold is spent. Keep patronage ceremonial: `-5`, treasury remains calm. |
| R05 | The Humanist Tutor | A humanist tutor argues that rulers should read history as instruction, not decoration. | Invite them to lecture: `+5`, nobles lose comfort. Keep tutors private: `-5`, court order holds. |
| R06 | Classics in the Market | Cheap copies of classical verses appear beside account books and salt fish. | Let the market read: `+5`, public opinion gains energy. Restrict copies to scholars: `-5`, elites approve. |
| R07 | Artist Versus Theologian | An artist and theologian quarrel over whether beauty teaches truth or distracts from it. | Defend artistic inquiry: `+10`, clergy satisfaction falls. Side with theology: `-10`, artists lose favor. |
| R08 | Court Masque of Renewal | Courtiers propose a grand performance celebrating rebirth, order, and the Crown's excellent taste. | Fund the masque: `+5`, prestige may rise. Avoid theatrical doctrine: `-5`, gold is saved. |
| R09 | A Ruin Measured | Surveyors measure ancient ruins and discover proportions that embarrass current builders. | Publish the measures: `+5`, engineers and artists approve. Treat them as antiquarian trivia: `-5`, no extra cost. |
| R10 | Women's Learning Salon | A salon of learned women circulates essays that make the Academy look smaller than it claims. | Welcome the essays: `+10`, conservative estates object. Dismiss the salon: `-10`, court traditionalists approve. |
| R11 | Translation of a Greek Text | A Greek text arrives with enough ambiguity to start three arguments and one school. | Sponsor translation: `+10`, gold is spent. Delay for review: `-5`, clergy and bureaucrats approve. |
| R12 | Fresco of the New Age | A fresco depicts the realm stepping from shadow into measured light. It is not subtle, which is why it works. | Place it in the Academy: `+5`, artists gain favor. Keep walls neutral: `-5`, conservative seats approve. |
| R13 | Old Workshop Resists | Traditional masters refuse new proportions, calling them foreign vanity. | Enforce the new curriculum: `+10`, guild satisfaction falls. Respect workshop custom: `-10`, burghers approve. |
| R14 | Poets at the Debate | Poets begin turning the issue into quotable lines, which may be useful and is definitely dangerous. | Use their language: `+5`, public opinion rises. Expel the poets: `-5`, seriousness is preserved. |
| R15 | The Prince's Portrait | The royal portraitist proposes painting the ruler in humanist style rather than sacred distance. | Accept the style: `+5`, prestige may rise. Keep the old iconography: `-5`, clergy approval rises. |
| R16 | New Calendar of Festivals | Scholars suggest reshaping civic festivals around learning, arts, and urban pride. | Adopt new festivals: `+10`, gold or stability is spent. Keep the old festival order: `-10`, clergy and local elders approve. |
| R17 | Imported Master | A foreign master offers techniques that local artists resent for being both foreign and better. | Hire the master: `+10`, artists gain skill but locals resent it. Decline politely: `-5`, local satisfaction rises. |
| R18 | Library Reordered | Humanists reorder the Academy library by subject instead of inherited shelf tradition. | Accept the order: `+5`, scholarly community approves. Restore old shelves: `-5`, conservative scholars approve. |
| R19 | The City as Classroom | Urban reformers argue that streets, squares, and facades can teach citizens better taste. | Back the urban program: `+10`, gold is spent. Keep art indoors: `-5`, treasury is spared. |
| R20 | Satire of the Old Masters | A biting satire makes old authorities look pompous, which is effective and slightly unfair. | Let satire circulate: `+5`, public opinion rises. Confiscate copies: `-10`, conservative approval rises. |

## Banking System Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| B01 | Double-Entry Demonstration | A merchant accountant proves that a ledger can expose lies without raising its voice. | Adopt double-entry standards: `+10`, burghers approve. Keep older accounts: `-5`, court clerks avoid disruption. |
| B02 | Noble Debt Roll | Bankers reveal how many noble estates survive on borrowed silence. | Use the roll as proof: `+10`, nobles lose satisfaction. Suppress the roll: `-10`, nobles approve. |
| B03 | Sermon on Usury | A popular preacher declares that interest eats souls faster than coin. | Defend regulated interest: `+5`, clergy satisfaction falls. Condemn the practice: `-10`, clergy approval rises. |
| B04 | Public Bank Proposal | Burghers propose a public bank under Crown guarantee, which sounds stable until everyone asks who guarantees the Crown. | Charter the bank: `+10`, legitimacy or gold is risked. Delay the charter: `-5`, conservative approval rises. |
| B05 | Debased Coin Panic | Rumors about coin quality turn market gossip into a lesson on monetary trust. | Reform the coinage: `+10`, treasury pays. Blame rumor-mongers: `-5`, order is preserved. |
| B06 | Widow's Deposit | A widow petitions after a private banker loses her dowry, making abstract regulation suddenly human. | Regulate deposits: `+5`, burghers accept oversight. Treat it as private misfortune: `-5`, bankers avoid limits. |
| B07 | Royal Loan Refusal | Bankers refuse an emergency royal loan unless banking law is clarified. | Clarify the law: `+10`, royal authority bends. Threaten the bankers: `-10`, legitimacy is protected. |
| B08 | Bills of Exchange | Merchants demonstrate that paper can move wealth faster than guarded carts. | Endorse bills of exchange: `+5`, trade interests approve. Restrict paper instruments: `-5`, conservative estates approve. |
| B09 | Fraudulent Ledger | A beautiful ledger is discovered to be a beautiful crime. | Use it to demand standards: `+10`, prestige is spent. Punish only the clerk: `-10`, elites avoid scrutiny. |
| B10 | Clerical Credit Chest | Monasteries and church offices reveal their own lending networks. | Bring them under law: `+5`, clergy satisfaction falls. Exempt religious credit: `-5`, clergy approve. |
| B11 | City Bank Riot | Debtors and creditors clash outside a city bank, each claiming justice and neither carrying it gently. | Mediate with new rules: `+5`, stability is spent. Close the bank temporarily: `-10`, order returns. |
| B12 | Tax Farm Accounts | Tax farmers object that transparent finance will make their profession less profitable, which is true. | Audit the farms: `+10`, nobles and contractors resent it. Preserve tax custom: `-10`, short-term revenue calms. |
| B13 | Scholar of Interest | A mathematician shows how compound interest works, and several listeners look personally accused. | Teach the method: `+5`, scholarly community approves. Keep the calculation obscure: `-5`, debtors approve. |
| B14 | Merchant Widow Fund | Burghers propose pooled insurance for sailors' families and failed caravans. | Recognize pooled risk: `+10`, burghers gain satisfaction. Reject novel liability: `-5`, conservative lawyers approve. |
| B15 | Foreign Banker Arrives | A foreign banking house offers expertise and a contract with too many neat clauses. | Invite them under regulation: `+5`, foreign influence grows. Keep banking domestic: `-5`, nobles approve. |
| B16 | Mint Officer's Confession | A mint officer admits the old system depends on tolerated confusion. | Publicize the confession: `+10`, legitimacy is strained. Retire them quietly: `-10`, stability is preserved. |
| B17 | Army Pay Delay | Soldiers go unpaid while treasurers debate methods, giving theory sharp boots. | Use banking reform to pay them: `+10`, military approves. Borrow informally again: `-5`, old creditors profit. |
| B18 | Contract in Plain Language | Reformers demand financial contracts ordinary people can read. | Require plain contracts: `+5`, public opinion approves. Keep elite legal forms: `-5`, lawyers and bankers approve. |
| B19 | Bankruptcy Shame | A merchant argues that orderly bankruptcy preserves trade better than public ruin. | Legalize orderly bankruptcy: `+10`, conservative moralists object. Keep disgrace as punishment: `-10`, clergy and nobles approve. |
| B20 | Crown Account Published | The Academy suggests publishing a simplified royal account to prove confidence in finance. | Publish it: `+10`, legitimacy is risked. Keep accounts closed: `-10`, court bureaucrats approve. |

## Discovery of the New World Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| NW01 | The Sailor's Chart | A battered chart shows coastlines that should not fit any known map, which is precisely the problem. | Trust the chart: `+10`, maritime merchants gain interest. Dismiss it as tavern ink: `-10`, conservatives approve. |
| NW02 | Returned Pilot | A pilot returns with salt, fever, and a story too consistent to ignore. | Hear them publicly: `+10`, exploration enthusiasm rises. Question them privately: `-5`, court caution holds. |
| NW03 | Clergy Ask for Mission Rights | Clerics insist discovery must begin as conversion, not commerce. | Grant mission priority: `-5`, clergy approve. Balance mission with survey: `+5`, clergy satisfaction falls. |
| NW04 | Merchants Want Charter | Merchants offer to fund voyages if they may name harbors before seeing them. | Issue a charter: `+10`, burghers gain satisfaction. Keep discovery under Crown lock: `-5`, legitimacy is preserved. |
| NW05 | Native Envoy's Account | A translated account from across the sea contradicts half the Academy's assumptions. | Let it reshape the debate: `+10`, conservatives object. Treat it as curiosity: `-10`, old geography survives. |
| NW06 | Disease Report | Physicians warn that new lands may bring sickness as well as maps. | Fund precautions and proceed: `+5`, gold is spent. Use disease as warning: `-5`, cautious estates approve. |
| NW07 | Missing Expedition | An expedition fails to return, and absence becomes an argument with excellent timing. | Continue the program: `+10`, prestige is risked. Suspend voyages: `-10`, families and clergy approve. |
| NW08 | Harbor Crowd | The harbor gathers to see strange goods unloaded, each object becoming a little ambassador. | Display the goods: `+5`, public opinion rises. Seal the cargo: `-5`, order is preserved. |
| NW09 | Mapmaker's Correction | A mapmaker erases a traditional boundary in front of witnesses. | Accept the correction: `+10`, scholarly authority shifts. Restore the old map: `-10`, conservatives approve. |
| NW10 | Naval Officers Demand Funds | Naval officers argue discovery is impossible while ships are treated as decorative wood. | Fund oceanic preparation: `+10`, gold is spent. Keep fleets coastal: `-5`, treasury calms. |
| NW11 | Rumor of Gold | Reports of gold spread faster than reliable latitude. | Use greed to fund voyages: `+5`, burghers approve but risk rises. Denounce the rumor: `-5`, clergy and nobles approve. |
| NW12 | Foreign Claim | A rival court claims the new coast first and sends letters full of confidence. | Contest the claim: `+10`, diplomacy is strained. Avoid provocation: `-10`, stability is preserved. |
| NW13 | Cosmographer's Error | The Academy's favored cosmographer admits a major distance estimate was wrong. | Praise correction as science: `+10`, scholar prestige is spent. Hide the error: `-10`, old authority survives. |
| NW14 | Sailors' Superstitions | Sailors refuse another voyage until omens are answered. | Pay and persuade them: `+5`, gold is spent. Accept their fear as wisdom: `-5`, clergy approval rises. |
| NW15 | Colonial Charter Abuse | A charter holder abuses distant authority before the principle has even won. | Reform charters: `+5`, burghers lose some freedom. Revoke the experiment: `-10`, conservatives approve. |
| NW16 | Imported Crop | A strange crop grows in a test garden and makes the unknown taste less theoretical. | Promote the crop: `+5`, peasants and merchants take interest. Keep it contained: `-5`, cautious estates approve. |
| NW17 | Treaty of Unknown Shores | Diplomats ask whether lands not fully known can already be divided by treaty. | Assert navigational rights: `+10`, foreign tension rises. Refuse distant entanglement: `-10`, court caution wins. |
| NW18 | Missionary Grammar | A missionary brings a grammar of a new language, proving that discovery has voices, not only coastlines. | Circulate the grammar: `+10`, clergy and scholars both gain interest. Keep it for missions only: `-5`, clergy control rises. |
| NW19 | Port Investors Panic | Investors panic after a storm destroys ships prepared for the next voyage. | Guarantee the expedition: `+10`, treasury is strained. Let investors retreat: `-10`, trade confidence falls. |
| NW20 | School Globe | A new globe in the Academy makes old maps look flat in every sense. | Make it public teaching: `+5`, public opinion rises. Keep it for experts: `-5`, elite control remains. |

## Printing Press Applications Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| P01 | First Run of Pamphlets | The first pamphlet run finishes before the censors finish deciding what a pamphlet is. | Distribute it widely: `+10`, public opinion surges. Confine it to scholars: `-5`, order is preserved. |
| P02 | Printer's Guild Petition | Printers ask for legal recognition before more presses appear in basements and borrowed kitchens. | Recognize the guild: `+10`, burghers gain satisfaction. Keep presses licensed case by case: `-5`, bureaucrats approve. |
| P03 | Clerical Index | Clergy propose an index of dangerous books, which the students immediately want to read. | Reject broad indexing: `+10`, clergy satisfaction falls. Approve the index: `-10`, clergy approval rises. |
| P04 | Cheap Prayer Sheets | Cheap printed prayer sheets reach villages faster than official sermons. | Use print for reform: `+5`, clergy control weakens. Restrict village printing: `-5`, clergy approve. |
| P05 | Scandal Sheet | A printer publishes court gossip beside serious argument and sells both equally well. | Defend press freedom: `+5`, legitimacy suffers. Punish the printer: `-10`, order rises. |
| P06 | Corrected Textbook | A printed textbook spreads corrected diagrams through schools in one season. | Adopt it: `+10`, scholarly community approves. Review it for another season: `-5`, conservatives approve. |
| P07 | Paper Shortage | Paper makers warn that debate cannot be printed on enthusiasm alone. | Subsidize paper: `+10`, gold is spent. Limit print runs: `-10`, treasury is spared. |
| P08 | Anonymous Broadsides | Anonymous broadsides support the issue with such vigor that even allies look nervous. | Tolerate them: `+5`, public opinion rises. Hunt the authors: `-5`, stability pressure eases. |
| P09 | Foreign Press Copies Us | A foreign press reprints Academy arguments with errors, insults, and impressive speed. | Answer in print: `+10`, prestige is spent. Ignore foreign noise: `-5`, diplomacy stays calmer. |
| P10 | Scribes' Protest | Scribes warn that movable type will starve honest hands and dishonest abbreviations alike. | Retrain scribes for presses: `+5`, gold is spent. Protect manuscript work: `-5`, old professions approve. |
| P11 | Royal Proclamation Printed | Officials discover that printed proclamations reach people before rumor edits them. | Standardize printed law: `+10`, bureaucrats gain efficiency. Keep proclamations traditional: `-5`, local elites approve. |
| P12 | Forbidden Book Success | A banned book becomes popular because it is banned, as books sometimes do out of spite. | Legalize and annotate it: `+10`, clergy satisfaction falls. Expand confiscations: `-10`, order rises. |
| P13 | University Printer | A university requests its own press to avoid begging city printers for sober priorities. | Grant the press: `+5`, scholars approve. Centralize printing: `-5`, bureaucrats approve. |
| P14 | Errors Multiply | One bad printed table spreads the same error through hundreds of copies. | Create correction sheets: `+5`, gold is spent. Use it against print reliability: `-5`, conservatives approve. |
| P15 | Ballad of the Issue | A printed ballad explains the debate badly but memorably. | Use popular print: `+5`, public opinion rises. Suppress vulgar argument: `-5`, elite approval rises. |
| P16 | Noble Libel Suit | A noble sues a printer for making old privilege look ridiculous in affordable type. | Protect the printer: `+10`, nobles lose satisfaction. Fine the printer: `-10`, nobles approve. |
| P17 | Multilingual Edition | Printers propose editions in several languages, making the argument harder to contain. | Publish them: `+10`, minorities and cities approve. Keep one official language: `-5`, central authority approves. |
| P18 | Press in the Barracks | Officers request printed drill manuals and technical sheets. | Approve military printing: `+5`, professional military approves. Keep presses civil: `-5`, conservative officers approve. |
| P19 | Printer Becomes Celebrity | A printer becomes famous enough to annoy scholars who wrote the actual words. | Use the fame: `+5`, burghers gain satisfaction. Recenter scholars: `-5`, scholarly community approves. |
| P20 | The Censor's Delay | The censor takes so long that the issue risks dying politely in a locked drawer. | Bypass the delay: `+10`, legitimacy is strained. Respect the process: `-10`, bureaucrats approve. |

## Confessionalism Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| C01 | Confession of the Court | Courtiers ask whether the Crown's faith should be displayed as policy or merely practiced as habit. | Make confession public policy: `+10`, nobles and reformers stir. Keep court faith private: `-10`, clergy factions calm. |
| C02 | Parish Registers | Reformers propose parish registers to make belief, marriage, and birth legible to the state. | Require registers: `+10`, bureaucrats approve but clergy resent oversight. Leave records local: `-5`, clergy approve. |
| C03 | Sermon Licensing | Preachers ask who may speak for doctrine when doctrine is becoming government. | License sermons centrally: `+5`, stability rises. Preserve local preaching custom: `-5`, local autonomy approves. |
| C04 | Noble Chapel Dispute | A noble house maintains a chapel practice that contradicts the emerging confession. | Enforce uniformity: `+10`, nobles lose satisfaction. Tolerate the chapel: `-10`, nobles approve. |
| C05 | Catechism Draft | Scholars produce a catechism short enough to be memorized and sharp enough to wound. | Print and teach it: `+10`, clergy factions react. Delay for consensus: `-5`, religious peace holds. |
| C06 | Minority Petition | A minority community asks whether confession means obedience or exclusion. | Define legal protection under confession: `+5`, minorities approve. Avoid guarantees: `-5`, conservative clergy approve. |
| C07 | Army Oath | Officers want a common oath to bind soldiers across province and parish. | Issue the oath: `+5`, professional military approves. Keep old oaths: `-5`, local estates approve. |
| C08 | Synod Summons | A synod is proposed to settle doctrine with enough witnesses that disagreement cannot hide. | Summon the synod: `+10`, gold and legitimacy are spent. Avoid spectacle: `-10`, stability is preserved. |
| C09 | Foreign Co-Religionists | Foreign co-religionists send support, advice, and the risk of being seen as sponsors. | Accept their letters: `+5`, foreign ties grow. Reject foreign influence: `-5`, nobles approve. |
| C10 | Feast Day Reform | Reformers want the calendar of holy days aligned with the state's confession. | Reform the calendar: `+10`, peasants and clergy may object. Keep local feasts: `-10`, local satisfaction rises. |
| C11 | Confessional Schoolbooks | Schoolbooks begin teaching doctrine as civic literacy. | Approve them: `+10`, public opinion shifts. Keep schools doctrinally local: `-5`, clergy autonomy remains. |
| C12 | Pilgrim Riot | A pilgrimage becomes a test of whether old devotion can coexist with new order. | Regulate the pilgrimage: `+5`, stability is spent. Let custom rule: `-5`, clergy approval rises. |
| C13 | Marriage Court | Jurists propose state-recognized marriage courts under confessional law. | Establish the courts: `+10`, bureaucrats approve. Leave marriage to existing clergy courts: `-10`, clergy approve. |
| C14 | Icon Debate | A church image becomes the center of argument over devotion, superstition, and obedience. | Set a confessional rule: `+5`, religious reformers approve. Avoid ruling: `-5`, local calm remains. |
| C15 | Border Preachers | Preachers crossing borders bring doctrine that is useful until diplomats notice. | Protect the preachers: `+10`, diplomatic tension rises. Restrain them: `-10`, foreign relations calm. |
| C16 | Confession Tax | Officials propose funding confessional schools through a dedicated levy. | Levy the tax: `+5`, gold rises but peasants object. Refuse the tax: `-5`, peasants approve. |
| C17 | Clergy Split | Clergy divide between old corporate privilege and new confessional discipline. | Back discipline: `+10`, clergy satisfaction falls. Back clerical privilege: `-10`, clergy approval rises. |
| C18 | Public Recantation | A prominent opponent offers to recant if spared humiliation. | Accept the recantation: `+5`, stability improves. Demand public shame: `+10`, opposition hardens. |
| C19 | Confessional Census | Bureaucrats ask to count communities by confession, turning faith into columns. | Count them: `+10`, minorities worry. Refuse the count: `-5`, local peace holds. |
| C20 | The Crown's Formula | Advisers draft a royal formula meant to sound eternal by tomorrow morning. | Proclaim it: `+10`, legitimacy is risked. Return it for revision: `-5`, no extra cost. |

## Global Trade Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| GT01 | Harbor Ledgers | Harbor ledgers show that the realm already lives by distant prices, whether nobles like it or not. | Read the ledgers aloud: `+10`, burghers approve. Dismiss merchant arithmetic: `-10`, nobles approve. |
| GT02 | Foreign Merchant Quarter | Foreign merchants request a protected quarter near the port. | Grant the quarter: `+10`, foreign influence grows. Refuse special rights: `-5`, local guilds approve. |
| GT03 | Tariff Confusion | Officials discover that current tariffs punish profitable trade mostly by accident. | Simplify tariffs: `+10`, bureaucrats lose old rents. Keep the schedule: `-5`, conservative officials approve. |
| GT04 | Spice Cargo | A spice cargo makes the old inland economy smell suddenly provincial. | Display the cargo: `+5`, public opinion and merchants stir. Tax it quietly: `-5`, treasury enjoys discretion. |
| GT05 | Port Nobles Object | Inland nobles claim ocean trade weakens honorable land-based wealth. | Challenge their claim: `+10`, nobles lose satisfaction. Reassure landed privilege: `-10`, nobles approve. |
| GT06 | Insurance for Ships | Merchants propose shared maritime insurance so one storm does not end ten fortunes. | Recognize maritime insurance: `+10`, burghers approve. Treat loss as private risk: `-5`, conservative moralists approve. |
| GT07 | Smuggler's Map | A captured smuggler's map shows a trade network more efficient than the legal one. | Reform legal routes: `+10`, corrupt officials resent it. Burn the map: `-10`, old controls remain. |
| GT08 | Dock Labor Strike | Dockworkers demand protection as trade expands faster than wages. | Negotiate protections: `+5`, peasants or workers approve. Break the strike: `-5`, merchants approve. |
| GT09 | Rival Trade Embassy | A rival sends merchants with gifts, contracts, and a smile trained in another court. | Receive them openly: `+5`, diplomacy deepens. Restrict their access: `-5`, protectionists approve. |
| GT10 | Standard Weights | Traders demand standard weights across markets because fraud has become too local to manage. | Standardize weights: `+10`, bureaucrats and merchants gain. Preserve local measures: `-10`, local autonomy approves. |
| GT11 | Caravan and Convoy | Inland caravan masters and sea captains argue over which route deserves state support. | Link caravan to convoy: `+10`, gold is spent. Keep route privileges separate: `-5`, old interests approve. |
| GT12 | Merchant School | Burghers propose teaching navigation, contracts, and languages as serious public knowledge. | Fund the school: `+10`, gold is spent. Leave training to families: `-5`, guild elders approve. |
| GT13 | Export Panic | A poor harvest makes exports look like treason to hungry towns. | Regulate but continue trade: `+5`, stability is spent. Halt exports broadly: `-10`, public anger cools. |
| GT14 | Port Quarantine | Quarantine officials slow trade and claim survival as their defense. | Improve quarantine systems: `+5`, gold is spent. Restrict foreign ships: `-5`, public safety feels visible. |
| GT15 | Naval Escort Debate | Merchants demand escorts and admirals demand funds, a partnership no one calls cheap. | Fund escorts: `+10`, treasury is strained. Let merchants self-insure: `-5`, state spending stays low. |
| GT16 | Guild Monopoly Challenge | Overseas traders challenge city guild monopolies as beautiful chains. | Break the monopoly: `+10`, guild satisfaction falls. Preserve guild privilege: `-10`, burghers split but old masters approve. |
| GT17 | Language of Contracts | Translators prove that bad contract language can sink profit without touching water. | Standardize trade languages: `+5`, scholars and merchants approve. Keep local contract forms: `-5`, local autonomy approves. |
| GT18 | Distant Price Shock | A price change abroad ruins local assumptions before local officials finish denying it. | Accept global exposure: `+10`, markets adjust painfully. Blame speculators: `-10`, public anger is redirected. |
| GT19 | Free Port Proposal | Reformers propose a free port where the Crown taxes flow instead of strangling it. | Charter the free port: `+10`, protectionists object. Reject the experiment: `-10`, old customs houses approve. |
| GT20 | Map of Trade Winds | Navigators present wind charts that make old routes look like superstition with sails. | Adopt wind routing: `+5`, maritime merchants approve. Keep established routes: `-5`, conservative captains approve. |

## Manufactories Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| MF01 | Workshop Under One Roof | A merchant shows how many hands can be made faster by sharing one roof and one bell. | Back the model: `+10`, guilds lose satisfaction. Keep dispersed workshops: `-10`, guilds approve. |
| MF02 | Guild Master's Complaint | Guild masters warn that scale makes bad work faster, which is not entirely false. | Enforce quality standards in manufactories: `+5`, gold is spent. Preserve guild inspection: `-5`, guilds approve. |
| MF03 | Waterwheel Proposal | Engineers propose a water-powered process that sounds less like craft and more like appetite. | Build the works: `+10`, local development is disrupted. Refuse mechanized pressure: `-10`, peasants approve. |
| MF04 | Women at the Looms | A manufactory hires women in numbers large enough to become a social argument. | Defend wage work: `+10`, conservative estates object. Restrict hiring custom: `-10`, clergy and guilds approve. |
| MF05 | Raw Material Bottleneck | Production stalls because raw material supply still thinks in village rhythm. | Organize supply contracts: `+5`, merchants approve. Limit production to supply custom: `-5`, rural interests approve. |
| MF06 | Fire in the Yard | A workshop fire becomes evidence either against concentration or against bad regulation. | Regulate manufactories: `+5`, gold is spent. Condemn large workshops: `-10`, guilds approve. |
| MF07 | Clock Discipline | Managers introduce bells and clocks, and workers discover time can become a supervisor. | Accept clock discipline: `+10`, peasants lose satisfaction. Limit work rules: `-5`, workers approve. |
| MF08 | Military Contract | The army offers a large contract if production can be standardized. | Accept standard production: `+10`, professional military approves. Keep bespoke supply: `-5`, old suppliers approve. |
| MF09 | Noble Estate Workshop | A noble estate opens a large workshop and then objects to burgher imitation. | Apply rules equally: `+10`, nobles lose satisfaction. Exempt noble workshops: `-10`, nobles approve. |
| MF10 | Child Labor Petition | Parish leaders object to children working in proto-factory conditions. | Set labor rules and continue: `+5`, clergy and peasants partly approve. Shut the model down: `-10`, conservative approval rises. |
| MF11 | Standard Parts | Artisans demonstrate interchangeable parts, and half the room is impressed while the other half mourns artistry. | Promote standard parts: `+10`, artists or guilds object. Keep craft variation: `-5`, guild satisfaction rises. |
| MF12 | Factory Accounts | Accountants show that large-scale production makes waste visible and therefore political. | Use the accounts: `+5`, bureaucrats approve. Avoid intrusive accounting: `-5`, workshop owners approve. |
| MF13 | Rural Displacement | Peasants complain that manufactory demand pulls hands from fields and daughters from households. | Manage transition: `+5`, gold or stability is spent. Slow expansion: `-10`, peasants approve. |
| MF14 | Imported Machine | A foreign machine arrives with unfamiliar bolts and very familiar ambition. | Copy and adapt it: `+10`, foreign tension or gold cost rises. Reject foreign machinery: `-10`, guilds approve. |
| MF15 | Coal Smoke Argument | Urban residents complain that productive smoke is still smoke. | Regulate smoke and continue: `+5`, gold is spent. Limit industrial sites: `-5`, local satisfaction rises. |
| MF16 | Piecework Pay | Owners propose piecework pay to reward output; workers hear a trap with arithmetic. | Permit regulated piecework: `+10`, worker satisfaction falls. Ban piecework: `-10`, peasants and guilds approve. |
| MF17 | Workshop School | Reformers propose training workers inside manufactories instead of through guild apprenticeship. | Fund workshop schools: `+10`, guilds lose satisfaction. Keep guild apprenticeship: `-10`, guilds approve. |
| MF18 | Quality Scandal | A large batch fails inspection, giving opponents exactly the failure they wanted. | Improve inspection and continue: `+5`, prestige is spent. Blame scale itself: `-5`, conservative seats approve. |
| MF19 | Merchant Capital Pool | Merchants pool capital to build a manufactory beyond one family's reach. | Legalize the pool: `+10`, banking interests approve. Forbid such concentration: `-10`, nobles and guilds approve. |
| MF20 | The First Whistle | A new factory whistle organizes the day so efficiently that everyone nearby hates it. | Defend the new discipline: `+5`, production supporters approve. Silence the whistle: `-5`, local calm rises. |

## Scientific Revolution Special Events

| ID | Title | Flavor | Options |
|---|---|---|---|
| SR01 | Table of Observations | A table of repeated observations refuses to flatter old authorities. | Trust repeated observation: `+10`, conservative scholars object. Treat it as anomaly: `-10`, old authority survives. |
| SR02 | Failed Replication | A celebrated result fails when repeated, which is embarrassing and useful in equal measure. | Publish the failure: `+10`, prestige is spent. Hide the failed trial: `-10`, reputation is protected. |
| SR03 | Mathematical Proof | A mathematician turns a natural question into symbols, and several officials look betrayed by clarity. | Accept mathematical method: `+10`, scholarly community approves. Demand plain tradition: `-5`, conservative seats approve. |
| SR04 | Instrument Maker's Claim | An instrument maker insists better tools make better truth, not merely better toys. | Fund new instruments: `+10`, gold is spent. Distrust tool-made claims: `-10`, old scholars approve. |
| SR05 | Academy Experiment Code | Reformers propose rules for witnessing, recording, and repeating experiments. | Adopt the code: `+10`, bureaucratic burden rises. Keep gentlemanly trust: `-5`, nobles approve. |
| SR06 | Clerical Cosmology Objection | Clergy warn that the new model will disorder more than the heavens. | Defend inquiry: `+10`, clergy satisfaction falls. Soften the model: `-10`, clergy approval rises. |
| SR07 | A Prediction Comes True | A calculation predicts a natural event accurately enough to make skeptics uncomfortable. | Publicize the prediction: `+10`, prestige rises with risk. Call it coincidence: `-10`, conservative calm returns. |
| SR08 | Laboratory Accident | A demonstration explodes loudly, proving at least that experiment is energetic. | Improve safety and continue: `+5`, gold is spent. Suspend experiments: `-10`, stability improves. |
| SR09 | Artisan Knowledge | An artisan solves a practical problem scholars had dressed in Latin. | Admit artisan evidence: `+10`, guild and scholar boundaries blur. Keep scholarly hierarchy: `-5`, elites approve. |
| SR10 | Natural History Cabinet | Collectors propose a cabinet of specimens arranged by observation rather than inherited categories. | Build the cabinet: `+5`, gold is spent. Keep old classifications: `-5`, conservative scholars approve. |
| SR11 | Open Correspondence | Scientists ask to publish letters and results across borders before rivals do. | Open correspondence: `+10`, foreign influence grows. Restrict exchange: `-10`, security-minded factions approve. |
| SR12 | Old Master Contradicted | A revered authority is contradicted in a footnote so polite it feels cruel. | Keep the footnote: `+10`, clergy or scholars object. Remove it: `-10`, old authority is protected. |
| SR13 | Public Demonstration | The Chief Scientist wants a public experiment where failure would be impossible to hide. | Hold it publicly: `+10`, prestige is risked. Keep trials private: `-5`, caution prevails. |
| SR14 | Measurement Standard | Researchers complain that every province measures nature with different tools and pride. | Standardize measurement: `+10`, gold is spent. Accept local measures: `-5`, local autonomy approves. |
| SR15 | Dissection of Error | Scholars propose studying errors as data, a suggestion that threatens many careers. | Record errors openly: `+5`, prestige is spent. Preserve reputations: `-5`, established scholars approve. |
| SR16 | Royal Observatory | Astronomers ask for a permanent observatory because the sky refuses to attend meetings indoors. | Build or fund it: `+10`, gold is spent. Use temporary observations: `-5`, treasury calms. |
| SR17 | Mechanic's Model | A mechanical model explains a natural process with gears, and the room leans forward despite itself. | Treat models as evidence: `+5`, artisans gain favor. Treat models as illustrations only: `-5`, scholars approve. |
| SR18 | Dangerous Publication | A treatise could overturn a doctrine but also offend nearly everyone who funds the Academy. | Publish it: `+10`, prestige and clergy satisfaction suffer. Delay publication: `-10`, patrons approve. |
| SR19 | Experimental Oath | Assistants ask for protection if results contradict patrons, teachers, or the Crown's favorite theory. | Protect the assistants: `+10`, legitimacy is strained. Require deference: `-10`, hierarchy approves. |
| SR20 | The New Method Named | Someone gives the method a name, and suddenly a cluster of habits becomes a movement. | Embrace the name: `+10`, opposition consolidates. Avoid naming it: `-5`, the debate stays softer. |

## Integration Notes

- The general-event pool should be checked before issue-specific events only for naming clarity; mechanically both may live in the same monthly event subpool.
- To keep the debate seat system central, most events should combine a progress delta with one small side effect rather than replacing the seat logic.
- The recommended conversion shape is one data-owned table for general events and one table keyed by issue for special events. Existing group, price, and stance helpers can be reused by implementation later, but this design does not require changing them now.
- Event text should present the progress change as an intellectual or political shift, while the option tooltip carries the exact `+5`, `+10`, `-5`, or `-10` progress.
