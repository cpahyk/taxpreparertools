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
    { name:"Matanuska-Susitna",      portal:"https://www.matsugov.us/assessor",                                                  methods:ALL,         notes:"Wasilla / Palmer area." },
    { name:"Fairbanks North Star",   portal:"https://fnsb.gov/153/Assessing",                                                    methods:ALL,         notes:"Fairbanks borough." }
  ],

  /* ───────────── ARIZONA ───────────── */
  AZ: [
    { name:"Maricopa",  portal:"https://mcassessor.maricopa.gov/",                                  methods:ALL,         notes:"Phoenix metro. Comprehensive search by all methods." },
    { name:"Pima",      portal:"https://www.asr.pima.gov/",                                          methods:ALL,         notes:"Tucson area. Free assessor portal." },
    { name:"Pinal",     portal:"https://www.pinalcountyaz.gov/Assessor/Pages/home.aspx",            methods:ALL,         notes:"Casa Grande / SE Phoenix metro." },
    { name:"Yavapai",   portal:"https://www.yavapaiaz.gov/Assessor",                                 methods:ALL,         notes:"Prescott / Sedona region." },
    { name:"Mohave",    portal:"https://www.mohave.gov/contentpage.aspx?id=29",                      methods:ALL,         notes:"Lake Havasu / Kingman." }
  ],

  /* ───────────── ARKANSAS ───────────── */
  AR: [
    { name:"Pulaski",    portal:"https://www.pulaskicountyassessor.net/",                            methods:ALL,         notes:"Little Rock. Free record search." },
    { name:"Benton",     portal:"https://bentoncountyar.gov/county-government/county-assessor/",     methods:ALL,         notes:"Bentonville / NW Arkansas." },
    { name:"Washington", portal:"https://www.co.washington.ar.us/government/departments-a-e/assessor", methods:ALL,         notes:"Fayetteville area." }
  ],

  /* ───────────── CALIFORNIA ───────────── */
  CA: [
    { name:"Los Angeles",     portal:"https://portal.assessor.lacounty.gov/parceldetail/",                         methods:ALL,         notes:"Largest county in the US. Use AIN or address." },
    { name:"San Diego",       portal:"https://arcc.sdcounty.ca.gov/Pages/Property-Search.aspx",                    methods:ALL,         notes:"Search by APN, address, or owner." },
    { name:"Orange",          portal:"https://ocgov.com/residents/property-tax",                                   methods:ALL,         notes:"Tax Collector + Assessor portals linked." },
    { name:"Riverside",       portal:"https://ca-riverside-ttc.publicaccessnow.com/",                              methods:ALL,         notes:"Treasurer-Tax Collector. Search & pay online." },
    { name:"San Bernardino",  portal:"https://mylandinfo.sbcounty.gov/",                                           methods:ALL,         notes:"MyLandInfo property portal." },
    { name:"Santa Clara",     portal:"https://www.sccassessor.org/",                                               methods:ALL,         notes:"San Jose / Silicon Valley." },
    { name:"Alameda",         portal:"https://www.acgov.org/ptax_pub_app/RealSearchInit.do",                       methods:ALL,         notes:"Oakland / East Bay tax search." },
    { name:"Sacramento",      portal:"https://eproptax.saccounty.gov/",                                            methods:ALL,         notes:"State capital region." },
    { name:"Contra Costa",    portal:"https://www.cccounty.us/assessor",                                           methods:ALL,         notes:"East Bay. Records + parcel viewer." },
    { name:"Fresno",          portal:"https://www.fresnocountyca.gov/Departments/Assessor-Recorder",               methods:ALL,         notes:"Central Valley." },
    { name:"Kern",            portal:"https://recorder.kerncounty.com/",                                           methods:ALL,         notes:"Bakersfield. Use Assessor link." },
    { name:"Ventura",         portal:"https://assessor.countyofventura.org/",                                      methods:ALL,         notes:"Coastal county north of LA." },
    { name:"San Francisco",   portal:"https://sfassessor.org/property-information/property-search",                methods:ALL,         notes:"City & County of SF." },
    { name:"San Mateo",       portal:"https://www.smcacre.gov/assessor",                                           methods:ALL,         notes:"Peninsula. Assessor-Recorder portal." },
    { name:"San Joaquin",     portal:"https://www.sjgov.org/department/asr",                                       methods:ALL,         notes:"Stockton area." },
    { name:"Stanislaus",      portal:"https://www.stancounty.com/assessor/",                                       methods:ALL,         notes:"Modesto." },
    { name:"Sonoma",          portal:"https://sonomacounty.ca.gov/clerk-recorder-assessor/assessor",               methods:ALL,         notes:"Wine country." },
    { name:"Tulare",          portal:"https://tularecounty.ca.gov/assessor/",                                      methods:ALL,         notes:"Visalia / Sequoia region." },
    { name:"Solano",          portal:"https://www.solanocounty.com/depts/ar/",                                     methods:ALL,         notes:"Vallejo / Fairfield." },
    { name:"Santa Barbara",   portal:"https://www.countyofsb.org/132/Assessor",                                    methods:ALL,         notes:"Coastal central." },
    { name:"Monterey",        portal:"https://www.countyofmonterey.gov/government/departments-a-h/assessor",      methods:ALL,         notes:"Salinas / Monterey Bay." },
    { name:"Placer",          portal:"https://www.placer.ca.gov/1791/Assessor",                                    methods:ALL,         notes:"Roseville / Tahoe gateway." },
    { name:"Marin",           portal:"https://www.marincounty.org/depts/ar",                                       methods:ALL,         notes:"North of Golden Gate." },
    { name:"Merced",          portal:"https://www.countyofmerced.com/151/Assessor",                                methods:ALL,         notes:"Central Valley." },
    { name:"Butte",           portal:"https://www.buttecounty.net/assessor",                                       methods:ALL,         notes:"Chico." }
  ],

  /* ───────────── COLORADO ───────────── */
  CO: [
    { name:"Denver",       portal:"https://www.denvergov.org/property/realproperty/search",     methods:ALL,         notes:"Real property search by address or schedule no." },
    { name:"El Paso",      portal:"https://assessor.elpasoco.com/",                              methods:ALL,         notes:"Colorado Springs." },
    { name:"Arapahoe",     portal:"https://www.arapahoegov.com/164/Assessor",                    methods:ALL,         notes:"Aurora / SE Denver metro." },
    { name:"Jefferson",    portal:"https://jeffco.us/2412/Assessor",                             methods:ALL,         notes:"West Denver suburbs." },
    { name:"Adams",        portal:"https://adcogov.org/assessor",                                methods:ALL,         notes:"North Denver metro." },
    { name:"Larimer",      portal:"https://www.larimer.gov/assessor",                            methods:ALL,         notes:"Fort Collins." },
    { name:"Douglas",      portal:"https://www.douglas.co.us/assessor/",                         methods:ALL,         notes:"Castle Rock / Highlands Ranch." },
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
    { name:"Sussex",      portal:"https://sussexcountyde.gov/property-search",                                  methods:ALL,         notes:"Beaches / S Delaware." },
    { name:"Kent",        portal:"https://www.co.kent.de.us/finance-dept/assessment-division.aspx",             methods:ALL,         notes:"Dover / Central." }
  ],

  /* ───────────── DC ───────────── */
  DC: [
    { name:"Washington DC", portal:"https://otr.cfo.dc.gov/page/real-property-tax-database-search",            methods:ALL,         notes:"DC Office of Tax & Revenue. SSL by address or square/suffix/lot." }
  ],

  /* ───────────── FLORIDA ───────────── */
  FL: [
    { name:"Miami-Dade",  portal:"https://www.miamidade.gov/Apps/PA/propertysearch/",                          methods:ALL,         notes:"Property Appraiser. Free, fast lookup." },
    { name:"Broward",     portal:"https://web.bcpa.net/bcpaclient/",                                            methods:ALL,         notes:"Fort Lauderdale. BCPA portal." },
    { name:"Palm Beach",  portal:"https://www.pbcgov.org/papa/",                                                methods:ALL,         notes:"PAPA - Property Appraiser Public Access." },
    { name:"Hillsborough",portal:"https://www.hcpafl.org/Property-Search",                                      methods:ALL,         notes:"Tampa." },
    { name:"Orange",      portal:"https://ocpaweb.ocpafl.org/parcelsearch",                                    methods:ALL,         notes:"Orlando." },
    { name:"Pinellas",    portal:"https://www.pcpao.gov/general-search",                                       methods:ALL,         notes:"St. Petersburg / Clearwater." },
    { name:"Duval",       portal:"https://paopropertysearch.coj.net/",                                          methods:ALL,         notes:"Jacksonville." },
    { name:"Lee",         portal:"https://www.leepa.org/",                                                      methods:ALL,         notes:"Fort Myers / Cape Coral." },
    { name:"Polk",        portal:"https://www.polkpa.org/CamaDisplay.aspx",                                     methods:ALL,         notes:"Lakeland / Winter Haven." },
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
    { name:"Gwinnett",   portal:"https://www.gwinnetttaxcommissioner.publicaccessnow.com/",                     methods:ALL,         notes:"NE Atlanta metro." },
    { name:"Cobb",       portal:"https://www.cobbtax.org/property",                                             methods:ALL,         notes:"NW Atlanta metro." },
    { name:"DeKalb",     portal:"https://publicaccess.dekalbcountyga.gov/",                                     methods:ALL,         notes:"E Atlanta / Decatur." },
    { name:"Clayton",    portal:"https://www.claytoncountyga.gov/government/tax-commissioner/",                 methods:ALL,         notes:"S Atlanta metro." },
    { name:"Cherokee",   portal:"https://www.cherokeega.com/Tax-Assessors-Office/",                             methods:ALL,         notes:"Canton / N Atlanta metro." },
    { name:"Henry",      portal:"https://qpublic.schneidercorp.com/Application.aspx?App=HenryCountyGA",         methods:ALL,         notes:"McDonough." },
    { name:"Forsyth",    portal:"https://www.forsythco.com/Departments-Offices/Board-of-Assessors",             methods:ALL,         notes:"Cumming." },
    { name:"Chatham",    portal:"https://www.chathamcountypa.org/",                                             methods:ALL,         notes:"Savannah." },
    { name:"Richmond",   portal:"https://www.augustaga.gov/4012/Assessors-Office",                              methods:ALL,         notes:"Augusta-Richmond consolidated." }
  ],

  /* ───────────── HAWAII ───────────── */
  HI: [
    { name:"Honolulu",   portal:"https://www.realpropertyhonolulu.com/",                                        methods:ALL,         notes:"Oahu (city + county)." },
    { name:"Hawaii",     portal:"https://www.hawaiipropertytax.com/",                                           methods:ALL,         notes:"Big Island." },
    { name:"Maui",       portal:"https://www.mauipropertytax.com/",                                             methods:ALL,         notes:"Maui, Lanai, Molokai." },
    { name:"Kauai",      portal:"https://www.kauai.gov/government/departments-agencies/finance/real-property", methods:ALL,         notes:"Kauai island." }
  ],

  /* ───────────── IDAHO ───────────── */
  ID: [
    { name:"Ada",        portal:"https://adacounty.id.gov/assessor/property-information/",                      methods:ALL,         notes:"Boise." },
    { name:"Canyon",     portal:"https://www.canyonco.org/elected-officials/assessor/",                         methods:ALL,         notes:"Nampa / Caldwell." },
    { name:"Kootenai",   portal:"https://www.kcgov.us/154/Assessor",                                            methods:ALL,         notes:"Coeur d'Alene." }
  ],

  /* ───────────── ILLINOIS ──────────
