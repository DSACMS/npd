-- SOURCED FROM Payer FHIR / JSON Data or from the PUFs/Google Searches etc.

CREATE TABLE "PayerToEndpoint" (
    "id" SERIAL PRIMARY KEY,
    "Payer_id" int   NOT NULL,
    "Endpoint_id" int   NOT NULL
);

CREATE TABLE "Payer" (
    -- marketplace/network-puf.IssuerID
    "id" SERIAL PRIMARY KEY,
    -- marketplace/plan-attributes-puf.IssuerMarketPlaceMarketingName
    "PayerName" varchar   NOT NULL
);

-- There are a lot of atributes for plans, not sure how much we need to include
CREATE TABLE "Plan" (
    -- marketplace/plan-attributes-puf.PlanId
    "id" SERIAL PRIMARY KEY,
    "Payer_id" int   NOT NULL,
    "MarketCoverage_id" int   NOT NULL,
    -- marketplace/plan-attributes-puf.ServiceAreaId
    "ServiceArea_id" int   NOT NULL,
    -- marketplace/plan-attributes-puf.DentalOnlyPlan
    "DentalOnlyPlan" boolean   NOT NULL,
    -- marketplace/plan-attributes-puf.PlanMarketingName
    "PlanMarketingName" varchar   NOT NULL,
    -- marketplace/plan-attributes-puf.HIOSProductId
    "HIOSProductID" varchar   NOT NULL,
    "PlanType_id" int   NOT NULL,
    -- marketplace/plan-attributes-puf.IsNewPlan
    "IsNewPlan" boolean   NOT NULL
);

CREATE TABLE "PlanType" (
    "id" SERIAL PRIMARY KEY,
    -- marketplace/plan-attributes-puf.PlanType
    "PlanType" varchar   NOT NULL
);

CREATE TABLE "MarketCoverage" (
    "id" SERIAL PRIMARY KEY,
    -- marketplace/plan-attributes-puf.MarketCoverage
    "MarketCoverage" varchar   NOT NULL
);

CREATE TABLE "NetworkToPlan" (
    "id" SERIAL PRIMARY KEY,
    "Plan_id" int   NOT NULL,
    "Network_id" int   NOT NULL
);

CREATE TABLE "Network" (
    -- marketplace/network-puf.NetworkID
    "id" SERIAL PRIMARY KEY,
    -- marketplace/network-puf.NetworkName
    "NetworkName" varchar   NOT NULL,
    -- marketplace/network-puf.NetworkURL
    "NetworkURL" varchar   NOT NULL
);

CREATE TABLE "ServiceArea" (
    -- marketplace/plan-attributes-puf.ServiceAreaId
    "id" SERIAL PRIMARY KEY,
    -- marketplace/service-area-puf.ServiceAreaName
    "ServiceAreaName" varchar   NOT NULL,
    -- marketplace/service-area-puf.StateCode
    "StateCode" varchar   NOT NULL,
    -- wishlist
    "shape" geometry   NOT NULL
);

-- PECOS Sourced initially, then UX Maintained
CREATE TABLE "NetworkToOrg" (
    "id" SERIAL PRIMARY KEY,
    "Network_id" int   NOT NULL,
    "Organization_id" int   NOT NULL
);
