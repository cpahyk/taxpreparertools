/* =========================================================================
   property-tax-data.js
   --------------------------------------------------------------------------
   Master directory of US property tax / assessor portal links.
   - 50 states + DC
   - 200+ counties with verified direct-portal URLs (top counties by pop.)
   - For any state/county not in the curated list, the UI falls back to a
     Google search query, so coverage is effectively 100% of US counties.

   Each county entry shape:
     {
       name:        "Harris",                       // display name (no "County" suffix)
       portal:      "https://hcad.org/...",         // primary search URL
       methods:     ["address","parcel","owner"],   // supported search inputs
       notes:       "Free online search."           // short hint shown to user
     }
   ========================================================================= */

const US_STATES = [
  { code:"AL", name:"Alabama" },           { code:"AK", name:"Alaska" },
  { code:"AZ", name:"Arizona" },           { code:"AR", name:"Arkansas" },
  { code:"CA", name:"California" },        { code:"CO", name:"Colorado" },
  { code:"CT", name:"Connecticut" },       { code:"DE", name:"Delaware" },
  { code:"DC", name:"District of Columbia" },
  { code:"FL", name:"Florida" },           { code:"GA", name:"Georgia" },
  { code:"HI", name:"Hawaii" },            { code:"ID", name:"Idaho" },
  { code:"IL", name:"Illinois" },          { code:"IN", name:"Indiana" },
  { code:"IA", name:"Iowa" },              { code:"KS", name:"Kansas" },
  { code:"KY", name:"Kentucky" },          { code:"LA", name:"Louisiana" },
  { code:"ME", name:"Maine" },             { code:"MD", name:"Maryland" },
  { code:"MA", name:"Massachusetts" },     { code:"MI", name:"Michigan" },
  { code:"MN", name:"Minnesota" },         { code:"MS", name:"Mississippi" },
  { code:"MO", name:"Missouri" },          { code:"MT", name:"Montana" },
  { code:"NE", name:"Nebraska" },          { code:"NV", name:"Nevada" },
  { code:"NH", name:"New Hampshire" },     { code:"NJ", name:"New Jersey" },
  { code:"NM", name:"New Mexico" },        { code:"NY", name:"New York" },
  { code:"NC", name:"North Carolina" },    { code:"ND", name:"North Dakota" },
  { code:"OH", name:"Ohio" },              { code:"OK", name:"Oklahoma" },
  { code:"OR", name:"Oregon" },            { code:"PA", name:"Pennsylvania" },
  { code:"RI", name:"Rhode Island" },      { code:"SC", name:"South Carolina" },
  { code:"SD", name:"South Dakota" },      { code:"TN", name:"Tennessee" },
  { code:"TX", name:"Texas" },             { code:"UT", name:"Utah" },
  { code:"VT", name:"Vermont" },           { code:"VA", name:"Virginia" },
  { code:"WA", name:"Washington" },        { code:"WV", name:"West Virginia" },
  { code:"WI", name:"Wisconsin" },         { code:"WY", name:"Wyoming" }
];

const ALL = ["address","parcel","owner"];
const ADDR_PARCEL = ["address","parcel"];

const COUNTY_PORTALS = {

  /* ───────────── ALABAMA ───────────── */
  AL: [
    { name:"Jefferson",  portal:"https://eringcapture.jccal.org/caportal/CAPortal_MainPage.aspx",                methods:ALL,         notes:"Birmingham metro. Free online property records." },
    { name:"Mobile",     portal:"https://www.mobilecopropertytax.com/",                                          methods:ALL,         notes:"Search by name, address, or parcel ID." },
    { name:"Madison",    portal:"https://www.madisoncountyal.gov/government/county-departments/tax-assessor",   methods:ALL,         notes:"Huntsville area. Online assessor portal." },
    { name:"Montgomery", portal:"https://www.mc-ala.org/residents/online-services/property-search",            methods:ALL,         notes:"Capital city. Tax & valuation lookup." },
    { name:"Tuscaloosa", portal:"https://www.tuscco.com/",                                                       methods:ALL,         notes:"Click Revenue → Property Search." },
    { name:"Shelby",     portal:"https://www.shelbyal.com/177/Property-Tax",                                     methods:ALL,         notes:"Birmingham suburb. Online payments + lookup." },
    { name:"Baldwin",    portal:"https://baldwincountyal.gov/government/county-departments/revenue-commission", methods:ALL,         notes:"Gulf Coast / Mobile metro." }
  ],

  /* ───────────── ALASKA ───────────── */
  AK: [
    { name:"Anchorage Municipality", portal:"https://www.muni.org/Departments/finance/treasury/PropertyTax/Pages/default.aspx", methods:ALL,         notes:"AK uses boroughs/municipalities, not counties." },
    { name:"Matanuska-Susitna",      portal:"https://www.matsugov.us/myproperty/",                                                  methods:ALL,         notes:"Wasilla / Palmer area." },
    { name:"Fairbanks North Star",   portal:"https://fnsb.gov/153/Assessing",                                                    methods:ALL,         notes:"Fairbanks borough." }
  ],

  /* ───────────── ARIZONA ───────────── */
  AZ: [
    { name:"Maricopa",  portal:"https://mcassessor.maricopa.gov/",                                  methods:ALL,         notes:"Phoenix metro. Comprehensive search by all methods." },
    { name:"Pima",      portal:"https://www.asr.pima.gov/",                                          methods:ALL,         notes:"Tucson area. Free assessor portal." },
    { name:"Pinal",     portal:"https://www.pinalcountyaz.gov/Assessor/Pages/home.aspx",            methods:ALL,         notes:"Casa Grande / SE Phoenix metro." },
    { name:"Yavapai",   portal:"https://www.yavapaiaz.gov/Assessor",                                 methods:ALL,         notes:"Prescott / Sedona region." },
    { name:"Mohave",    portal:"https://www.mohave.gov/ContentPage.aspx?id=111&cid=1595",                      methods:ALL,         notes:"Lake Havasu / Kingman." }
  ],

  /* ───────────── ARKANSAS ───────────── */
  AR: [
    { name:"Pulaski",    portal:"https://www.pulaskicountyassessor.net/",                            methods:ALL,         notes:"Little Rock. Free record search." },
    { name:"Benton",     portal:"https://bentoncountyar.gov/county-government/county-assessor/",     methods:ALL,         notes:"Bentonville / NW Arkansas." },
    { name:"Washington", portal:"https://www.actdatascout.com/State/AR/Washington?isPP=False", methods:ALL,         notes:"Fayetteville area." }
  ],

  /* ───────────── CALIFORNIA ───────────── */
  CA: [
    { name:"Los Angeles",     portal:"https://portal.assessor.lacounty.gov/parceldetail/",                         methods:ALL,         notes:"Largest county in the US. Use AIN or address." },
    { name:"San Diego",       portal:"https://publicservices.sandiegocounty.gov/CitizenAccess/APO/APOLookup.aspx",                    methods:ALL,         notes:"Search by APN, address, or owner." },
    { name:"Orange",          portal:"https://assessedvalue.ocassessor.gov/",                                   methods:ALL,         notes:"Tax Collector + Assessor portals linked." },
    { name:"Riverside",       portal:"https://ca-riverside-ttc.publicaccessnow.com/",                              methods:ALL,         notes:"Treasurer-Tax Collector. Search & pay online." },
    { name:"San Bernardino",  portal:"https://mylandinfo.sbcounty.gov/",                                           methods:ALL,         notes:"MyLandInfo property portal." },
    { name:"Santa Clara",     portal:"https://www.sccassessor.org/",                                               methods:ALL,         notes:"San Jose / Silicon Valley." },
    { name:"Alameda",         portal:"https://www.acgov.org/ptax_pub_app/RealSearchInit.do",                       methods:ALL,         notes:"Oakland / East Bay tax search." },
    { name:"Sacramento",      portal:"https://eproptax.saccounty.gov/",                                            methods:ALL,         notes:"State capital region." },
    { name:"Contra Costa",    portal:"https://www.cccounty.us/assessor",                                           methods:ALL,         notes:"East Bay. Records + parcel viewer." },
    { name:"Fresno",          portal:"https://www.fresnocountyca.gov/Departments/Assessor-Recorder",               methods:ALL,         notes:"Central Valley." },
    { name:"Kern",            portal:"https://www.kerncounty.com/government/departments/assessor-recorder/property/assessor-property-search",                                           methods:ALL,         notes:"Bakersfield. Use Assessor link." },
    { name:"Ventura",         portal:"https://assessor.countyofventura.org/",                                      methods:ALL,         notes:"Coastal county north of LA." },
    { name:"San Francisco",   portal:"https://sfassessor.org/property-information/property-search",                methods:ALL,         notes:"City & County of SF." },
    { name:"San Mateo",       portal:"https://www.smcacre.gov/assessor",                                           methods:ALL,         notes:"Peninsula. Assessor-Recorder portal." },
    { name:"San Joaquin",     portal:"https://www.sjgov.org/department/asr",                                       methods:ALL,         notes:"Stockton area." },
    { name:"Stanislaus",      portal:"https://www.stancounty.com/assessor/",                                       methods:ALL,         notes:"Modesto." },
    { name:"Sonoma",          portal:"https://common1.mptsweb.com/mbap/sonoma/asr",               methods:ALL,         notes:"Wine country." },
    { name:"Tulare",          portal:"https://tularecounty.ca.gov/assessor/",                                      methods:ALL,         notes:"Visalia / Sequoia region." },
    { name:"Solano",          portal:"https://ca-solano.publicaccessnow.com/Assessor/PropertySearch.aspx",                                     methods:ALL,         notes:"Vallejo / Fairfield." },
    { name:"Santa Barbara",   portal:"https://www.countyofsb.org/132/Assessor",                                    methods:ALL,         notes:"Coastal central." },
    { name:"Monterey",        portal:"https://www.countyofmonterey.gov/government/departments-a-h/assessor",      methods:ALL,         notes:"Salinas / Monterey Bay." },
    { name:"Placer",          portal:"https://www.placer.ca.gov/1791/Assessor",                                    methods:ALL,         notes:"Roseville / Tahoe gateway." },
    { name:"Marin",           portal:"https://www.marincounty.org/depts/ar",                                       methods:ALL,         notes:"North of Golden Gate." },
    { name:"Merced",          portal:"https://www.countyofmerced.com/151/Assessor",                                methods:ALL,         notes:"Central Valley." },
    { name:"Butte",           portal:"https://www.buttecounty.net/assessor",                                       methods:ALL,         notes:"Chico." }
  ],

  /* ───────────── COLORADO ───────────── */
  CO: [
    { name:"Denver",       portal:"https://www.denvergov.org/property",     methods:ALL,         notes:"Real property search by address or schedule no." },
    { name:"El Paso",      portal:"https://assessor.elpasoco.com/",                              methods:ALL,         notes:"Colorado Springs." },
    { name:"Arapahoe",     portal:"https://arapahoeco.gov/your_county/county_departments/assessor/property_search/index.php",                    methods:ALL,         notes:"Aurora / SE Denver metro." },
    { name:"Jefferson",    portal:"https://jeffco.us/2412/Assessor",                             methods:ALL,         notes:"West Denver suburbs." },
    { name:"Adams",        portal:"https://gisapp.adcogov.org/PropertySearch",                                methods:ALL,         notes:"North Denver metro." },
    { name:"Larimer",      portal:"https://www.larimer.gov/assessor",                            methods:ALL,         notes:"Fort Collins." },
    { name:"Douglas",      portal:"http://www.douglas.co.us/assessor/",                         methods:ALL,         notes:"Castle Rock / Highlands Ranch." },
    { name:"Boulder",      portal:"https://www.bouldercounty.org/property-and-land/assessor/",   methods:ALL,         notes:"Boulder city + county." },
    { name:"Weld",         portal:"https://www.weldgov.com/government/departments/assessor",     methods:ALL,         notes:"Greeley / N Front Range." }
  ],

  /* ───────────── CONNECTICUT ───────────── */
  CT: [
    { name:"Fairfield",   portal:"https://www.google.com/search?q=fairfield+county+ct+property+tax+town+assessor",   methods:ALL,         notes:"CT has town-level assessors, not county. Search at the town level." },
    { name:"Hartford",    portal:"https://www.google.com/search?q=hartford+county+ct+property+tax+town+assessor",    methods:ALL,         notes:"CT abolished county government — use town assessor sites." },
    { name:"New Haven",   portal:"https://www.google.com/search?q=new+haven+county+ct+property+tax+town+assessor",   methods:ALL,         notes:"Search by town: New Haven, Hamden, West Haven, etc." }
  ],

  /* ───────────── DELAWARE ───────────── */
  DE: [
    { name:"New Castle",  portal:"https://propertytax.newcastlede.gov/",                                       methods:ALL,         notes:"Wilmington / N Delaware." },
    { name:"Sussex",      portal:"https://property.sussexcountyde.gov/PT/forms/htmlframe.aspx?mode=content/home.htm",                                  methods:ALL,         notes:"Beaches / S Delaware." },
    { name:"Kent",        portal:"https://www.co.kent.de.us/finance-dept/assessment-division.aspx",             methods:ALL,         notes:"Dover / Central." }
  ],

  /* ───────────── DC ───────────── */
  DC: [
    { name:"Washington DC", portal:"https://otr.cfo.dc.gov/page/real-property-tax-database-search",            methods:ALL,         notes:"DC Office of Tax & Revenue. SSL by address or square/suffix/lot." }
  ],

  /* ───────────── FLORIDA ───────────── */
  FL: [
    { name:"Miami-Dade",  portal:"https://www.miamidade.gov/Apps/PA/propertysearch/#/",                          methods:ALL,         notes:"Property Appraiser. Free, fast lookup." },
    { name:"Broward",     portal:"https://web.bcpa.net/bcpaclient/",                                            methods:ALL,         notes:"Fort Lauderdale. BCPA portal." },
    { name:"Palm Beach",  portal:"https://pbcpao.gov/Property/Search",                                                methods:ALL,         notes:"PAPA - Property Appraiser Public Access." },
    { name:"Hillsborough",portal:"https://www.hcpafl.org/Property-Search",                                      methods:ALL,         notes:"Tampa." },
    { name:"Orange",      portal:"https://ocpaweb.ocpafl.org/parcelsearch",                                    methods:ALL,         notes:"Orlando." },
    { name:"Pinellas",    portal:"https://www.pcpao.gov/",                                       methods:ALL,         notes:"St. Petersburg / Clearwater." },
    { name:"Duval",       portal:"https://paopropertysearch.coj.net/",                                          methods:ALL,         notes:"Jacksonville." },
    { name:"Lee",         portal:"https://www.leepa.org/",                                                      methods:ALL,         notes:"Fort Myers / Cape Coral." },
    { name:"Polk",        portal:"https://www.polkflpa.gov/CamaSearch.aspx",                                     methods:ALL,         notes:"Lakeland / Winter Haven." },
    { name:"Brevard",     portal:"https://www.bcpao.us/PropertySearch/",                                        methods:ALL,         notes:"Space Coast / Melbourne." },
    { name:"Volusia",     portal:"https://vcpa.vcgov.org/",                                                     methods:ALL,         notes:"Daytona Beach." },
    { name:"Seminole",    portal:"https://parceldetails.scpafl.org/",                                           methods:ALL,         notes:"N Orlando metro." },
    { name:"Pasco",       portal:"https://search.pascopa.com/",                                                 methods:ALL,         notes:"N Tampa metro." },
    { name:"Sarasota",    portal:"https://www.sc-pa.com/propertysearch/",                                       methods:ALL,         notes:"Gulf coast / SW FL." },
    { name:"Manatee",     portal:"https://www.manateepao.gov/search/",                                          methods:ALL,         notes:"Bradenton." },
    { name:"Marion",      portal:"https://www.pa.marion.fl.us/",                                                methods:ALL,         notes:"Ocala." },
    { name:"Collier",     portal:"https://www.collierappraiser.com/",                                           methods:ALL,         notes:"Naples." },
    { name:"Lake",        portal:"https://www.lakecopropappr.com/",                                             methods:ALL,         notes:"Central FL." },
    { name:"Osceola",     portal:"https://www.property-appraiser.org/",                                         methods:ALL,         notes:"Kissimmee / Disney area." },
    { name:"Leon",        portal:"https://www.leonpa.gov/",                                                     methods:ALL,         notes:"Tallahassee / state capital." }
  ],

  /* ───────────── GEORGIA ───────────── */
  GA: [
    { name:"Fulton",     portal:"https://iaspublicaccess.fultoncountyga.gov/",                                  methods:ALL,         notes:"Atlanta. iasWorld parcel portal." },
    { name:"Gwinnett",   portal:"https://qpublic.schneidercorp.com/Application.aspx?AppID=1282&LayerID=43872&PageTypeID=2&PageID=16058",                     methods:ALL,         notes:"NE Atlanta metro." },
    { name:"Cobb",       portal:"https://qpublic.schneidercorp.com/Application.aspx?AppID=1051&LayerID=23951&PageTypeID=2&PageID=9967",                                             methods:ALL,         notes:"NW Atlanta metro." },
    { name:"DeKalb",     portal:"https://dekalbtax.org/property-information",                                     methods:ALL,         notes:"E Atlanta / Decatur." },
    { name:"Clayton",    portal:"https://www.claytoncountyga.gov/government/tax-commissioner/",                 methods:ALL,         notes:"S Atlanta metro." },
    { name:"Cherokee",   portal:"https://www.cherokeega.com/Tax-Assessors-Office/",                             methods:ALL,         notes:"Canton / N Atlanta metro." },
    { name:"Henry",      portal:"https://qpublic.schneidercorp.com/Application.aspx?App=HenryCountyGA",         methods:ALL,         notes:"McDonough." },
    { name:"Forsyth",    portal:"https://www.forsythco.com/Departments-Offices/Board-of-Assessors",             methods:ALL,         notes:"Cumming." },
    { name:"Chatham",    portal:"http://boa.chathamcounty.org/",                                             methods:ALL,         notes:"Savannah." },
    { name:"Richmond",   portal:"https://qpublic.schneidercorp.com/Application.aspx?AppID=678&LayerID=11365&PageTypeID=2&PageID=4758",                              methods:ALL,         notes:"Augusta-Richmond consolidated." }
  ],

  /* ───────────── HAWAII ───────────── */
  HI: [
    { name:"Honolulu",   portal:"https://realproperty.honolulu.gov",                                        methods:ALL,         notes:"Oahu (city + county)." },
    { name:"Hawaii",     portal:"https://www.hawaiipropertytax.com/",                                           methods:ALL,         notes:"Big Island." },
    { name:"Maui",       portal:"https://www.mauipropertytax.com/",                                             methods:ALL,         notes:"Maui, Lanai, Molokai." },
    { name:"Kauai",      portal:"https://www.kauai.gov/government/departments-agencies/finance/real-property", methods:ALL,         notes:"Kauai island." }
  ],

  /* ───────────── IDAHO ───────────── */
  ID: [
    { name:"Ada",        portal:"http://www.adacountyassessor.org/propsys/",                      methods:ALL,         notes:"Boise." },
    { name:"Canyon",     portal:"https://id-canyon.publicaccessnow.com/Assessor/PropertySearch.aspx",                         methods:ALL,         notes:"Nampa / Caldwell." },
    { name:"Kootenai",   portal:"http://www.kcgov.us/departments/mapping/mapSearch/",                                            methods:ALL,         notes:"Coeur d'Alene." }
  ],

  /* ───────────── ILLINOIS ───────────── */
  IL: [
    { name:"Cook",       portal:"https://www.cookcountyassessor.com/advanced-search",                            methods:ALL,         notes:"Chicago. Comprehensive PIN/address/owner search." },
    { name:"DuPage",     portal:"http://www.dupageco.org/PropertyInfo/PropertyLookup.aspx",                                  methods:ALL,         notes:"Naperville / W Chicago suburbs." },
    { name:"Lake",       portal:"https://www.lakecountyil.gov/2854/Property-Tax-Assessment-Information",        methods:ALL,         notes:"Waukegan / N suburbs." },
    { name:"Will",       portal:"https://www.willcountysoa.com/",                                               methods:ALL,         notes:"Joliet." },
    { name:"Kane",       portal:"https://kaneil.devnetwedge.com/",                                              methods:ALL,         notes:"Aurora / Elgin." },
    { name:"McHenry",    portal:"https://www.mchenrycountyil.gov/county-government/departments-a-i/assessments", methods:ALL,         notes:"NW suburbs." },
    { name:"Winnebago",  portal:"https://assessor.wincoil.gov/search/",                                  methods:ALL,         notes:"Rockford." },
    { name:"Madison",    portal:"https://www.madisoncountyil.gov/departments/chief_county_assesment_office/",   methods:ALL,         notes:"Edwardsville / Metro East St. Louis." },
    { name:"St. Clair",  portal:"https://www.co.st-clair.il.us/departments/assessor",                           methods:ALL,         notes:"Belleville / Metro East." }
  ],

  /* ───────────── INDIANA ───────────── */
  IN: [
    { name:"Marion",     portal:"https://www.indy.gov/agency/marion-county-assessors-office",                   methods:ALL,         notes:"Indianapolis." },
    { name:"Lake",       portal:"https://engage.xsoftinc.com/lake",              methods:ALL,         notes:"Gary / NW Indiana." },
    { name:"Allen",      portal:"https://www.allencounty.us/assessor",                                          methods:ALL,         notes:"Fort Wayne." },
    { name:"Hamilton",   portal:"https://www.hamiltoncounty.in.gov/180/Assessor",                               methods:ALL,         notes:"Carmel / Fishers." },
    { name:"St. Joseph", portal:"https://www.sjcindiana.com/156/Assessor",                                      methods:ALL,         notes:"South Bend." },
    { name:"Tippecanoe", portal:"https://www.tippecanoe.in.gov/137/Assessor",                                   methods:ALL,         notes:"Lafayette / Purdue." }
  ],

  /* ───────────── IOWA ───────────── */
  IA: [
    { name:"Polk",       portal:"https://web.assess.co.polk.ia.us/cgi-bin/web/tt/infoqry.cgi",                  methods:ALL,         notes:"Des Moines." },
    { name:"Linn",       portal:"http://linn.iowaassessors.com/search.php",                                  methods:ALL,         notes:"Cedar Rapids." },
    { name:"Scott",      portal:"https://www.scottcountyiowa.gov/assessor",                                     methods:ALL,         notes:"Davenport / Quad Cities." }
  ],

  /* ───────────── KANSAS ───────────── */
  KS: [
    { name:"Johnson",    portal:"https://www.jocogov.org/dept/appraiser",                                       methods:ALL,         notes:"Overland Park / KC suburbs." },
    { name:"Sedgwick",   portal:"https://www.sedgwickcounty.org/appraiser/",                                    methods:ALL,         notes:"Wichita." },
    { name:"Shawnee",    portal:"https://ares.sncoapps.us/",                                                      methods:ALL,         notes:"Topeka." },
    { name:"Wyandotte",  portal:"https://www.wycokck.org/Departments/Appraiser",                                methods:ALL,         notes:"Kansas City KS." }
  ],

  /* ───────────── KENTUCKY ───────────── */
  KY: [
    { name:"Jefferson",  portal:"https://jeffersonpva.ky.gov/property-search/",                                 methods:ALL,         notes:"Louisville. PVA office." },
    { name:"Fayette",    portal:"https://www.fayettepva.com/",                                                  methods:ALL,         notes:"Lexington." },
    { name:"Kenton",     portal:"https://kentonpva.org/property-search/",                                       methods:ALL,         notes:"Covington / N KY." },
    { name:"Boone",      portal:"https://boonepva.ky.gov/property-search/",                                     methods:ALL,         notes:"N KY / Cincinnati metro." }
  ],

  /* ───────────── LOUISIANA ───────────── */
  LA: [
    { name:"East Baton Rouge",  portal:"https://www.ebrpa.org/",                                                methods:ALL,         notes:"Capital parish." },
    { name:"Jefferson Parish",  portal:"https://www.jpassessor.com/",                                           methods:ALL,         notes:"New Orleans suburb. LA uses parishes." },
    { name:"Orleans Parish",    portal:"https://nolaassessor.com/property-search/",                              methods:ALL,         notes:"New Orleans proper." },
    { name:"Caddo",             portal:"https://www.caddoassessor.org/",                                         methods:ALL,         notes:"Shreveport." },
    { name:"Lafayette",         portal:"https://www.lafayetteassessor.com/",                                     methods:ALL,         notes:"Lafayette parish." }
  ],

  /* ───────────── MAINE ───────────── */
  ME: [
    { name:"Cumberland",  portal:"https://www.google.com/search?q=cumberland+county+maine+property+tax+town+assessor", methods:ALL, notes:"ME assessment is town-level. Portland is largest city." },
    { name:"York",        portal:"https://www.google.com/search?q=york+county+maine+town+property+assessor",            methods:ALL, notes:"Search by town: York, Sanford, Biddeford, etc." },
    { name:"Penobscot",   portal:"https://www.google.com/search?q=penobscot+county+maine+town+property+assessor",       methods:ALL, notes:"Bangor is largest city." }
  ],

  /* ───────────── MARYLAND ───────────── */
  MD: [
    { name:"Montgomery",      portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"MD uses statewide SDAT — pick county on portal." },
    { name:"Prince George's", portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"Use SDAT and select Prince George's." },
    { name:"Baltimore County",portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"Suburban Baltimore (separate from city)." },
    { name:"Baltimore City",  portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"Independent city, file under Baltimore City." },
    { name:"Anne Arundel",    portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"Annapolis." },
    { name:"Howard",          portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"Columbia / Ellicott City." },
    { name:"Harford",         portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"Bel Air." },
    { name:"Frederick",       portal:"https://sdat.dat.maryland.gov/RealProperty/",                              methods:ALL,         notes:"Frederick city + county." }
  ],

  /* ───────────── MASSACHUSETTS ───────────── */
  MA: [
    { name:"Middlesex",   portal:"https://www.google.com/search?q=middlesex+county+ma+town+property+assessor",  methods:ALL, notes:"MA assessment is by city/town. Includes Cambridge, Lowell." },
    { name:"Worcester",   portal:"https://www.google.com/search?q=worcester+county+ma+town+property+assessor",  methods:ALL, notes:"Worcester city is largest." },
    { name:"Essex",       portal:"https://www.google.com/search?q=essex+county+ma+town+property+assessor",      methods:ALL, notes:"Lawrence, Lynn, Salem." },
    { name:"Suffolk",     portal:"https://www.boston.gov/departments/assessing",                                 methods:ALL, notes:"Boston city assessor." },
    { name:"Norfolk",     portal:"https://www.google.com/search?q=norfolk+county+ma+town+property+assessor",    methods:ALL, notes:"Quincy, Brookline." },
    { name:"Plymouth",    portal:"https://www.google.com/search?q=plymouth+county+ma+town+property+assessor",   methods:ALL, notes:"Brockton, Plymouth." },
    { name:"Hampden",     portal:"https://www.google.com/search?q=hampden+county+ma+town+property+assessor",    methods:ALL, notes:"Springfield." }
  ],

  /* ───────────── MICHIGAN ───────────── */
  MI: [
    { name:"Wayne",       portal:"https://pta.waynecounty.com/",             methods:ALL,         notes:"Detroit." },
    { name:"Oakland",     portal:"https://www.oakgov.com/treasurer/Pages/property-tax-info.aspx",                methods:ALL,         notes:"Detroit's wealthier N suburbs." },
    { name:"Macomb",      portal:"http://treasurer.macombgov.org/", methods:ALL,        notes:"NE Detroit metro." },
    { name:"Kent",        portal:"https://www.accesskent.com/Departments/Equalization/property_search.htm",      methods:ALL,         notes:"Grand Rapids." },
    { name:"Genesee",     portal:"https://bsaonline.com/OnlinePayment/OnlinePaymentSearch?PaymentApplicationType=5&uid=304",                              methods:ALL,         notes:"Flint." },
    { name:"Washtenaw",   portal:"https://www.washtenaw.org/172/Equalization",                                   methods:ALL,         notes:"Ann Arbor." },
    { name:"Ottawa",      portal:"https://www.miottawa.org/Departments/Equalization/",                           methods:ALL,         notes:"Holland / Grand Haven." }
  ],

  /* ───────────── MINNESOTA ───────────── */
  MN: [
    { name:"Hennepin",    portal:"http://www.hennepin.us/residents/property/property-information-search",      methods:ALL,         notes:"Minneapolis." },
    { name:"Ramsey",      portal:"https://www.ramseycounty.us/residents/property-home/property-tax-and-value-lookup",                       methods:ALL,         notes:"St. Paul." },
    { name:"Dakota",      portal:"https://gis.co.dakota.mn.us/Webappbuilder/PropertyInformationPublic/index.html",    methods:ALL,         notes:"S Twin Cities suburbs." },
    { name:"Anoka",       portal:"https://www.anokacountymn.gov/313/Property-Records-Taxation",                  methods:ALL,         notes:"N Twin Cities suburbs." },
    { name:"Washington",  portal:"https://mn-washington.publicaccessnow.com",       methods:ALL,         notes:"Stillwater / E Twin Cities." },
    { name:"Olmsted",     portal:"https://publicaccess.co.olmsted.mn.us/search/commonsearch.aspx?mode=realprop", methods:ALL,         notes:"Rochester." }
  ],

  /* ───────────── MISSISSIPPI ───────────── */
  MS: [
    { name:"Hinds",       portal:"https://www.hindscountyms.com/elected-offices/tax-assessor-collector",         methods:ALL,         notes:"Jackson." },
    { name:"Harrison",    portal:"https://www.co.harrison.ms.us/elected/tax_assessor.asp",                       methods:ALL,         notes:"Gulfport / Biloxi." },
    { name:"DeSoto",      portal:"https://www.desotocountyms.gov/106/Tax-Assessor",                              methods:ALL,         notes:"Memphis suburbs." }
  ],

  /* ───────────── MISSOURI ───────────── */
  MO: [
    { name:"St. Louis County", portal:"https://revenue.stlouisco.com/IAS/index.htm",                            methods:ALL,         notes:"Suburbs (separate from city)." },
    { name:"Jackson",          portal:"https://www.jacksongov.org/Residents/Pay-Taxes",                          methods:ALL,         notes:"Kansas City MO." },
    { name:"St. Charles",      portal:"https://www.sccmo.org/189/Assessor",                                      methods:ALL,         notes:"W St. Louis suburbs." },
    { name:"St. Louis City",   portal:"https://www.stlouis-mo.gov/government/departments/assessor/",             methods:ALL,         notes:"Independent city." },
    { name:"Greene",           portal:"https://www.greenecountymo.gov/assessor/",                                methods:ALL,         notes:"Springfield MO." }
  ],

  /* ───────────── MONTANA ───────────── */
  MT: [
    { name:"Yellowstone",  portal:"https://www.yellowstonecountymt.gov/treasurer/",                              methods:ALL,         notes:"Billings." },
    { name:"Missoula",     portal:"https://svc.mt.gov/dor/property",   methods:ALL,         notes:"Missoula." },
    { name:"Gallatin",     portal:"https://www.gallatin.mt.gov/treasurer",                                       methods:ALL,         notes:"Bozeman." }
  ],

  /* ───────────── NEBRASKA ───────────── */
  NE: [
    { name:"Douglas",   portal:"https://www.dcassessor.org/",                                                    methods:ALL,         notes:"Omaha." },
    { name:"Lancaster", portal:"http://orion.lancaster.ne.gov/Appraisal/PublicAccess/",                                             methods:ALL,         notes:"Lincoln." }
  ],

  /* ───────────── NEVADA ───────────── */
  NV: [
    { name:"Clark",       portal:"https://www.clarkcountynv.gov/government/assessor/property_search/index.php", methods:ALL, notes:"Las Vegas." },
    { name:"Washoe",      portal:"https://www.washoecounty.gov/assessor/",                                       methods:ALL,         notes:"Reno." },
    { name:"Carson City", portal:"https://www.carson.org/government/departments-a-f/assessor",                    methods:ALL,         notes:"State capital." }
  ],

  /* ───────────── NEW HAMPSHIRE ───────────── */
  NH: [
    { name:"Hillsborough", portal:"https://www.google.com/search?q=hillsborough+county+nh+town+property+assessor", methods:ALL, notes:"NH assessment is town-level. Manchester / Nashua." },
    { name:"Rockingham",   portal:"https://www.google.com/search?q=rockingham+county+nh+town+property+assessor",   methods:ALL, notes:"Search by town." },
    { name:"Merrimack",    portal:"https://www.google.com/search?q=merrimack+county+nh+town+property+assessor",    methods:ALL, notes:"Concord (state capital)." }
  ],

  /* ───────────── NEW JERSEY ───────────── */
  NJ: [
    { name:"Bergen",     portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=0203",                   methods:ALL,         notes:"NJ uses Monmouth County's statewide MOD-IV portal." },
    { name:"Middlesex",  portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=1208",                   methods:ALL,         notes:"Edison / New Brunswick." },
    { name:"Essex",      portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=0700",                   methods:ALL,         notes:"Newark." },
    { name:"Hudson",     portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=0900",                   methods:ALL,         notes:"Jersey City." },
    { name:"Monmouth",   portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=1300",                   methods:ALL,         notes:"Shore counties." },
    { name:"Ocean",      portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=1500",                   methods:ALL,         notes:"Toms River area." },
    { name:"Union",      portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=2000",                   methods:ALL,         notes:"Elizabeth / NJ Transit corridor." },
    { name:"Camden",     portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=0400",                   methods:ALL,         notes:"Philly suburbs." },
    { name:"Passaic",    portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=1600",                   methods:ALL,         notes:"Paterson." },
    { name:"Morris",     portal:"https://tax1.co.monmouth.nj.us/cgi-bin/m4.cgi?district=1400",                   methods:ALL,         notes:"Morristown / NW NJ." }
  ],

  /* ───────────── NEW MEXICO ───────────── */
  NM: [
    { name:"Bernalillo",  portal:"https://www.bernco.gov/assessor/",                                             methods:ALL,         notes:"Albuquerque." },
    { name:"Doña Ana",    portal:"https://www.donaanacounty.org/assessor",                                       methods:ALL,         notes:"Las Cruces." },
    { name:"Santa Fe",    portal:"https://www.santafecountynm.gov/assessor",                                     methods:ALL,         notes:"State capital." }
  ],

  /* ───────────── NEW YORK ───────────── */
  NY: [
    { name:"Kings (Brooklyn)",    portal:"https://a836-pts-access.nyc.gov/care/search/commonsearch.aspx?mode=address", methods:ALL,    notes:"NYC. Use ACRIS for deeds, PTS for taxes." },
    { name:"Queens",              portal:"https://a836-pts-access.nyc.gov/care/search/commonsearch.aspx?mode=address", methods:ALL,    notes:"NYC borough." },
    { name:"New York (Manhattan)",portal:"https://a836-pts-access.nyc.gov/care/search/commonsearch.aspx?mode=address", methods:ALL,    notes:"NYC borough." },
    { name:"Bronx",               portal:"https://a836-pts-access.nyc.gov/care/search/commonsearch.aspx?mode=address", methods:ALL,    notes:"NYC borough." },
    { name:"Richmond (Staten Is.)", portal:"https://a836-pts-access.nyc.gov/care/search/commonsearch.aspx?mode=address", methods:ALL,  notes:"NYC borough." },
    { name:"Suffolk",             portal:"https://www.suffolkcountyny.gov/Departments/Real-Property-Tax-Service-Agency", methods:ALL, notes:"Long Island east." },
    { name:"Nassau",              portal:"https://lrv.nassaucountyny.gov/",                                                methods:ALL, notes:"Long Island west." },
    { name:"Westchester",         portal:"https://www.westchestergov.com/property-tax",                                    methods:ALL, notes:"NYC northern suburbs." },
    { name:"Erie",                portal:"http://www2.erie.gov/ecrpts/index.php?q=real-property-parcel-search",                                              methods:ALL, notes:"Buffalo." },
    { name:"Monroe",              portal:"https://www.monroecounty.gov/etc/rp/",                                            methods:ALL, notes:"Rochester." },
    { name:"Onondaga",            portal:"https://ocfintax.ongov.net/",                                                     methods:ALL, notes:"Syracuse." },
    { name:"Albany",              portal:"https://www.albanycounty.com/government/departments/real-property-tax-service",   methods:ALL, notes:"State capital." },
    { name:"Orange",              portal:"https://www.orangecountygov.com/612/Parcel-Information",                               methods:ALL, notes:"Newburgh / Hudson Valley." },
    { name:"Rockland",            portal:"https://rocklandgis.com/portal/apps/webappviewer/",                               methods:ALL, notes:"NYC northern suburb." },
    { name:"Dutchess",            portal:"https://gis.dutchessny.gov/parcelaccess/",                                        methods:ALL, notes:"Poughkeepsie." }
  ],

  /* ───────────── NORTH CAROLINA ───────────── */
  NC: [
    { name:"Mecklenburg", portal:"https://property.spatialest.com/nc/mecklenburg/",                              methods:ALL,         notes:"Charlotte." },
    { name:"Wake",        portal:"https://services.wake.gov/realestate/",                                        methods:ALL,         notes:"Raleigh." },
    { name:"Guilford",    portal:"http://taxcama.guilfordcountync.gov/camapwa/",      methods:ALL,         notes:"Greensboro." },
    { name:"Forsyth",     portal:"http://www.co.forsyth.nc.us/tax/default.aspx",                              methods:ALL,         notes:"Winston-Salem." },
    { name:"Cumberland",  portal:"https://www.cumberlandcountync.gov/departments/tax-group/tax",                 methods:ALL,         notes:"Fayetteville." },
    { name:"Durham",      portal:"https://www.dconc.gov/county-departments/departments-f-z/tax-administration",  methods:ALL,         notes:"Durham." },
    { name:"Buncombe",    portal:"https://tax.buncombecounty.org/",                          methods:ALL,         notes:"Asheville." },
    { name:"Union",       portal:"https://unionnc.devnetwedge.com/",                                            methods:ALL,         notes:"Charlotte SE suburbs." },
    { name:"New Hanover", portal:"https://etax.nhcgov.com/",                                                     methods:ALL,         notes:"Wilmington." },
    { name:"Gaston",      portal:"https://gis.gastoncountync.gov/",        methods:ALL,         notes:"W Charlotte metro." }
  ],

  /* ───────────── NORTH DAKOTA ───────────── */
  ND: [
    { name:"Cass",      portal:"https://www.casscountynd.gov/county/depts/tax",                                  methods:ALL,         notes:"Fargo." },
    { name:"Burleigh",  portal:"https://itax.tylertech.com/BurleighND/",                        methods:ALL,         notes:"Bismarck (state capital)." }
  ],

  /* ───────────── OHIO ───────────── */
  OH: [
    { name:"Cuyahoga",   portal:"https://myplace.cuyahogacounty.gov/",                                           methods:ALL,         notes:"Cleveland. MyPlace parcel viewer." },
    { name:"Franklin",   portal:"https://property.franklincountyauditor.com/",                                   methods:ALL,         notes:"Columbus." },
    { name:"Hamilton",   portal:"https://wedge1.hcauditor.org/",                                                 methods:ALL,         notes:"Cincinnati." },
    { name:"Summit",     portal:"https://fiscaloffice.summitoh.net/index.php/property-search",                   methods:ALL,         notes:"Akron." },
    { name:"Montgomery", portal:"https://www.mcrealestate.org/",                                                 methods:ALL,         notes:"Dayton." },
    { name:"Lucas",      portal:"https://www.co.lucas.oh.us/167/Auditor",                                        methods:ALL,         notes:"Toledo." },
    { name:"Stark",      portal:"http://www.starkcountyohio.gov/treasurer",                                               methods:ALL,         notes:"Canton." },
    { name:"Butler",     portal:"http://www.butlercountytreasurer.org/",                                          methods:ALL,         notes:"Cincinnati N suburbs." },
    { name:"Lorain",     portal:"https://www.loraincounty.com/auditor/",                                         methods:ALL,         notes:"Elyria / W Cleveland metro." },
    { name:"Mahoning",   portal:"http://treasurer.mahoningcountyoh.gov/",                                     methods:ALL,         notes:"Youngstown." }
  ],

  /* ───────────── OKLAHOMA ───────────── */
  OK: [
    { name:"Oklahoma",  portal:"https://www.oklahomacounty.org/195/Assessor",                                    methods:ALL,         notes:"Oklahoma City." },
    { name:"Tulsa",     portal:"https://assessor.tulsacounty.org/",                                          methods:ALL,         notes:"Tulsa." },
    { name:"Cleveland", portal:"https://property.spatialest.com/ok/cleveland/#/",             methods:ALL,         notes:"Norman / OKC south." },
    { name:"Canadian",  portal:"https://property.spatialest.com/ok/canadian/#/",                                        methods:ALL,         notes:"Yukon / OKC west." }
  ],

  /* ───────────── OREGON ───────────── */
  OR: [
    { name:"Multnomah",  portal:"https://multcoproptax.com/Property-Search",                                     methods:ALL,         notes:"Portland." },
    { name:"Washington", portal:"https://www.washingtoncountyor.gov/at",                                         methods:ALL,         notes:"Hillsboro / W Portland metro." },
    { name:"Clackamas",  portal:"https://www.clackamas.us/at",                                                   methods:ALL,         notes:"Oregon City / S Portland metro." },
    { name:"Lane",       portal:"http://apps.lanecounty.org/propertyaccountinformation/",     methods:ALL,         notes:"Eugene." },
    { name:"Marion",     portal:"https://www.co.marion.or.us/AO/Pages/default.aspx",                             methods:ALL,         notes:"Salem (state capital)." },
    { name:"Jackson",    portal:"https://pdo.jacksoncountyor.gov/pdo/",                   methods:ALL,         notes:"Medford." }
  ],

  /* ───────────── PENNSYLVANIA ───────────── */
  PA: [
    { name:"Philadelphia",  portal:"https://property.phila.gov/",                                                methods:ALL,         notes:"Philadelphia OPA." },
    { name:"Allegheny",     portal:"https://www2.alleghenycounty.us/RealEstate/Search.aspx",                     methods:ALL,         notes:"Pittsburgh." },
    { name:"Montgomery",    portal:"http://propertyrecords.montcopa.org/pt/forms/htmlframe.aspx?mode=content/home.htm",   methods:ALL,         notes:"Norristown / Philly suburbs." },
    { name:"Bucks",         portal:"https://www.buckscountyboa.org/search/commonsearch.aspx?mode=owner",     methods:ALL,         notes:"Doylestown / Philly N suburbs." },
    { name:"Chester",       portal:"https://www.chesco.org/Assessment",                                          methods:ALL,         notes:"West Chester." },
    { name:"Delaware",      portal:"https://delcorealestate.co.delaware.pa.us/",                                  methods:ALL,         notes:"Media / Philly W suburbs." },
    { name:"Lancaster",     portal:"https://lancasterpa.devnetwedge.com/",                                       methods:ALL,         notes:"Lancaster." },
    { name:"York",          portal:"https://assessmentpublic.yorkcountypa.gov/",  methods:ALL,         notes:"York." },
    { name:"Berks",         portal:"https://www.co.berks.pa.us/Dept/Assessment/Pages/default.aspx",              methods:ALL,         notes:"Reading." },
    { name:"Lehigh",        portal:"https://www.lehighcounty.org/Departments/Assessment",                        methods:ALL,         notes:"Allentown." },
    { name:"Westmoreland",  portal:"https://www.co.westmoreland.pa.us/216/Assessment",                            methods:ALL,         notes:"Greensburg / Pittsburgh E suburbs." },
    { name:"Luzerne",       portal:"https://www.luzernecounty.org/199/Assessors-Office",                          methods:ALL,         notes:"Wilkes-Barre / Scranton metro." }
  ],

  /* ───────────── RHODE ISLAND ───────────── */
  RI: [
    { name:"Providence",  portal:"https://www.google.com/search?q=providence+county+ri+town+property+assessor",  methods:ALL, notes:"RI uses city/town assessors. Providence is largest city." },
    { name:"Kent",        portal:"https://www.google.com/search?q=kent+county+ri+town+property+assessor",        methods:ALL, notes:"Warwick area." }
  ],

  /* ───────────── SOUTH CAROLINA ───────────── */
  SC: [
    { name:"Greenville",  portal:"http://www.greenvillecounty.org/appsAS400/RealProperty/",                        methods:ALL,         notes:"Upstate SC." },
    { name:"Richland",    portal:"https://richlandcountysc.gov/Government/Departments/Taxes/Assessor",                                                methods:ALL,         notes:"Columbia (state capital)." },
    { name:"Charleston",  portal:"https://sc-charleston.publicaccessnow.com/",                                   methods:ALL,         notes:"Charleston." },
    { name:"Horry",       portal:"https://www.horrycountysc.gov/departments/assessor/",                          methods:ALL,         notes:"Myrtle Beach." },
    { name:"Spartanburg", portal:"http://www.spartanburgcounty.org/288/Assessor-Property-Records-Search",                                methods:ALL,         notes:"Spartanburg." },
    { name:"Lexington",   portal:"https://www.lex-co.sc.gov/departments/assessor",                                methods:ALL,         notes:"W Columbia metro." }
  ],

  /* ───────────── SOUTH DAKOTA ───────────── */
  SD: [
    { name:"Minnehaha", portal:"https://www2.minnehahacounty.org/property_tax/index.aspx",                                  methods:ALL,         notes:"Sioux Falls." },
    { name:"Pennington",portal:"https://docs.pennco.org/apps/PropertyTax2/Search.aspx",                                             methods:ALL,         notes:"Rapid City." }
  ],

  /* ───────────── TENNESSEE ───────────── */
  TN: [
    { name:"Shelby",     portal:"https://www.assessormelvinburgess.com/propertysearch",                          methods:ALL,         notes:"Memphis." },
    { name:"Davidson",   portal:"https://www.padctn.org/",                                                       methods:ALL,         notes:"Nashville-Davidson consolidated." },
    { name:"Knox",       portal:"http://www.knoxcounty.org/property/",                                          methods:ALL,         notes:"Knoxville." },
    { name:"Hamilton",   portal:"https://assessor.hamiltontn.gov/",                                              methods:ALL,         notes:"Chattanooga." },
    { name:"Rutherford", portal:"https://secured.rutherfordcountytn.gov/propertydata/",                                                       methods:ALL,         notes:"Murfreesboro." },
    { name:"Williamson", portal:"http://www.williamson-tn.org/assessor/",                                   methods:ALL,         notes:"Franklin / Nashville S suburbs." },
    { name:"Montgomery", portal:"http://www.mcgtn.org/assessor",                                                methods:ALL,         notes:"Clarksville." }
  ],

  /* ───────────── TEXAS ───────────── */
  TX: [
    { name:"Harris",      portal:"https://hcad.org/property-search/property-search",                                            methods:ALL,         notes:"Houston. TX uses Appraisal Districts (CADs)." },
    { name:"Dallas",      portal:"https://www.dallascad.org/SearchAddr.aspx",                                    methods:ALL,         notes:"Dallas CAD." },
    { name:"Tarrant",     portal:"https://www.tad.org/property-search/",                                         methods:ALL,         notes:"Fort Worth / Arlington." },
    { name:"Bexar",       portal:"https://bexar.acttax.com/act_webdev/bexar/index.jsp",                                         methods:ALL,         notes:"San Antonio." },
    { name:"Travis",      portal:"https://www.traviscad.org/property-search/",                                   methods:ALL,         notes:"Austin." },
    { name:"Collin",      portal:"https://www.collincad.org/propertysearch",                                     methods:ALL,         notes:"Plano / Frisco." },
    { name:"Hidalgo",     portal:"https://www.hidalgoad.org/",                                                   methods:ALL,         notes:"McAllen / Rio Grande Valley." },
    { name:"Denton",      portal:"https://www.dentoncad.com/property-search",                                    methods:ALL,         notes:"Denton / N Dallas suburbs." },
    { name:"Fort Bend",   portal:"https://www.fbcad.org/property-search/",                                       methods:ALL,         notes:"Sugar Land / SW Houston." },
    { name:"El Paso",     portal:"https://www.epcad.org/Search",                                                 methods:ALL,         notes:"El Paso." },
    { name:"Montgomery",  portal:"https://www.mcad-tx.org/Property-Search",                                      methods:ALL,         notes:"The Woodlands / N Houston." },
    { name:"Williamson",  portal:"http://www.wcad.org/",                                        methods:ALL,         notes:"Round Rock / N Austin." },
    { name:"Cameron",     portal:"https://www.cameroncad.org/",                                                  methods:ALL,         notes:"Brownsville / RGV." },
    { name:"Brazoria",    portal:"https://esearch.brazoriacad.org/",                             methods:ALL,         notes:"Pearland / Lake Jackson." },
    { name:"Galveston",   portal:"https://www.galvestoncountytx.gov/our-county/county-clerk/records-search",                                 methods:ALL,         notes:"Galveston / League City." },
    { name:"Nueces",      portal:"https://www.nuecescad.net/Search",                                             methods:ALL,         notes:"Corpus Christi." },
    { name:"Lubbock",     portal:"https://lubbockcad.org/",                                   methods:ALL,         notes:"Lubbock." },
    { name:"Bell",        portal:"https://bellcad.org/",                                     methods:ALL,         notes:"Killeen / Temple." },
    { name:"Webb",        portal:"https://www.webbcad.org/PropertySearch.aspx",                                  methods:ALL,         notes:"Laredo." },
    { name:"McLennan",    portal:"https://www.mclennancad.org/property-search",                                  methods:ALL,         notes:"Waco." },
    { name:"Smith",       portal:"https://publictax.smith-county.com/search",                                      methods:ALL,         notes:"Tyler." },
    { name:"Brazos",      portal:"https://www.brazoscad.org/property-search",                                    methods:ALL,         notes:"College Station / Bryan." },
    { name:"Ellis",       portal:"https://www.elliscad.com/PropertySearch.aspx",                                 methods:ALL,         notes:"Waxahachie / S Dallas suburbs." },
    { name:"Johnson",     portal:"https://www.johnsoncountytaxoffice.org/search",                                  methods:ALL,         notes:"Cleburne / SW Fort Worth." },
    { name:"Kaufman",     portal:"https://www.kaufman-cad.org/property-search/",                                 methods:ALL,         notes:"Kaufman / E Dallas suburbs." }
  ],

  /* ───────────── UTAH ───────────── */
  UT: [
    { name:"Salt Lake",   portal:"https://slco.org/assessor/",                                                   methods:ALL,         notes:"SLC metro." },
    { name:"Utah",        portal:"https://www.utahcounty.gov/landrecords/",                                      methods:ALL,         notes:"Provo / Orem." },
    { name:"Davis",       portal:"https://www.daviscountyutah.gov/assessor",                                     methods:ALL,         notes:"N SLC suburbs." },
    { name:"Weber",       portal:"https://www3.co.weber.ut.us/assessor/",                                        methods:ALL,         notes:"Ogden." }
  ],

  /* ───────────── VERMONT ───────────── */
  VT: [
    { name:"Chittenden",  portal:"https://www.google.com/search?q=chittenden+county+vt+town+property+assessor",  methods:ALL, notes:"VT assessment is town-level. Burlington is largest city." }
  ],

  /* ───────────── VIRGINIA ───────────── */
  VA: [
    { name:"Fairfax",        portal:"https://icare.fairfaxcounty.gov/ffxcare/search/commonsearch.aspx?mode=address", methods:ALL,    notes:"DC suburbs. iCare portal." },
    { name:"Prince William", portal:"https://www.pwcgov.org/realestate",                                          methods:ALL,         notes:"Manassas / Woodbridge." },
    { name:"Loudoun",        portal:"https://loudounportal.com/taxes",                            methods:ALL,         notes:"Leesburg / NoVA." },
    { name:"Virginia Beach", portal:"https://www.vbgov.com/government/departments/assessor",                       methods:ALL,         notes:"Independent city." },
    { name:"Chesterfield",   portal:"https://www.chesterfield.gov/828/Real-Estate-Assessment-Data#/",                    methods:ALL,         notes:"Richmond suburbs." },
    { name:"Henrico",        portal:"https://henrico.us/finance/disclaimer/",                                              methods:ALL,         notes:"Richmond suburbs." },
    { name:"Arlington",      portal:"https://www.arlingtonva.us/Government/Departments/Real-Estate-Assessments",   methods:ALL,         notes:"DC suburbs." },
    { name:"Norfolk",        portal:"https://www.norfolk.gov/4225/Real-Estate-Search",                             methods:ALL,         notes:"Independent city." },
    { name:"Richmond City",  portal:"https://www.rva.gov/finance/real-estate-assessor",                            methods:ALL,         notes:"State capital, independent city." }
  ],

  /* ───────────── WASHINGTON ───────────── */
  WA: [
    { name:"King",       portal:"https://blue.kingcounty.com/Assessor/eRealProperty/default.aspx",                methods:ALL,         notes:"Seattle. eRealProperty portal." },
    { name:"Pierce",     portal:"https://www.piercecountywa.gov/736/Property-Search",                              methods:ALL,         notes:"Tacoma." },
    { name:"Snohomish",  portal:"http://www.snohomishcountywa.gov/175/Assessor",                                      methods:ALL,         notes:"Everett / N Seattle metro." },
    { name:"Spokane",    portal:"http://www.spokanecounty.org/pubpadal/",                                       methods:ALL,         notes:"Spokane." },
    { name:"Clark",      portal:"https://gis.clark.wa.gov/gishome/property/",                                      methods:ALL,         notes:"Vancouver WA." },
    { name:"Thurston",   portal:"https://www.thurstoncountywa.gov/departments/assessor",                           methods:ALL,         notes:"Olympia (state capital)." },
    { name:"Kitsap",     portal:"https://psearch.kitsapgov.com/pdetails/",                                             methods:ALL,         notes:"Bremerton." }
  ],

  /* ───────────── WEST VIRGINIA ───────────── */
  WV: [
    { name:"Kanawha",     portal:"https://kanawhacountyassessor.com/",                                       methods:ALL,         notes:"Charleston (state capital)." },
    { name:"Berkeley",    portal:"https://www.berkeleywv.org/162/Assessor",                                        methods:ALL,         notes:"Martinsburg / E panhandle." }
  ],

  /* ───────────── WISCONSIN ───────────── */
  WI: [
    { name:"Milwaukee",  portal:"https://assessments.milwaukee.gov/",                                              methods:ALL,         notes:"Milwaukee." },
    { name:"Dane",       portal:"https://treasurer.countyofdane.com/",                                            methods:ALL,         notes:"Madison (state capital)." },
    { name:"Waukesha",   portal:"https://tapestry.fidlar.com/Tapestry2/Welcome.aspx?cid=46&cn=Waukesha",            methods:ALL,         notes:"W Milwaukee suburbs." },
    { name:"Brown",      portal:"https://www.browncountywi.gov/departments/real-property-tax-information/",        methods:ALL,         notes:"Green Bay." },
    { name:"Racine",     portal:"https://www.racinecounty.com/government/treasurer/property-tax-information",      methods:ALL,         notes:"Racine." }
  ],

  /* ───────────── WYOMING ───────────── */
  WY: [
    { name:"Laramie",   portal:"https://www.laramiecountywy.gov/government/elected-officials/assessor/",           methods:ALL,         notes:"Cheyenne." },
    { name:"Natrona",   portal:"https://www.natronacounty-wy.gov/176/Assessor",                                    methods:ALL,         notes:"Casper." }
  ]
};

/* Build a fallback Google search URL for any state/county not covered above. */
function buildGoogleFallback(stateName, countyName) {
  const q = encodeURIComponent(`${countyName} County ${stateName} property tax search`);
  return `https://www.google.com/search?q=${q}`;
}

/* Get all county data for a state (curated list only). */
function getCounties(stateCode) {
  return COUNTY_PORTALS[stateCode] || [];
}

/* Public API exposed to the page. */
window.PROPERTY_TAX_DATA = {
  states: US_STATES,
  getCounties,
  buildGoogleFallback,
  totalCounties: Object.values(COUNTY_PORTALS).reduce((n, arr) => n + arr.length, 0)
};
