import { COVER_PAGE_TEMPLATE, STANDARD_TERMS_TEMPLATE } from "./templates";
import { NdaFormData } from "./types";

function renderTemplate(template: string, values: Record<string, string>): string {
  return template.replace(/{{(\w+)}}/g, (match, token: string) =>
    token in values ? values[token] : match,
  );
}

function formatDate(isoDate: string): string {
  if (!isoDate) return "[Effective Date]";
  const date = new Date(`${isoDate}T00:00:00`);
  if (Number.isNaN(date.getTime())) return isoDate;
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function orBlank(value: string, placeholder: string): string {
  return value.trim() ? value.trim() : placeholder;
}

function mndaTermChecklist(data: NdaFormData): string {
  const years = data.termYears || 1;
  const fixedChecked = data.termType === "fixed" ? "x" : " ";
  const untilChecked = data.termType === "until-terminated" ? "x" : " ";
  return [
    `- [${fixedChecked}] Expires ${years} year(s) from Effective Date.`,
    `- [${untilChecked}] Continues until terminated in accordance with the terms of the MNDA.`,
  ].join("\n");
}

function confidentialityChecklist(data: NdaFormData): string {
  const years = data.confidentialityYears || 1;
  const fixedChecked = data.confidentialityType === "fixed" ? "x" : " ";
  const perpetuityChecked = data.confidentialityType === "perpetuity" ? "x" : " ";
  return [
    `- [${fixedChecked}] ${years} year(s) from Effective Date, but in the case of trade secrets until Confidential Information is no longer considered a trade secret under applicable laws.`,
    `- [${perpetuityChecked}] In perpetuity.`,
  ].join("\n");
}

function mndaTermPhrase(data: NdaFormData): string {
  return data.termType === "fixed"
    ? `${data.termYears || 1} year(s) from the Effective Date`
    : "period ending upon termination by either party in accordance with the terms of the MNDA";
}

function confidentialityTermPhrase(data: NdaFormData): string {
  return data.confidentialityType === "fixed"
    ? `${data.confidentialityYears || 1} year(s) from the Effective Date`
    : "in perpetuity";
}

export interface GeneratedNda {
  coverPage: string;
  standardTerms: string;
  full: string;
}

export function buildNdaDocument(data: NdaFormData): GeneratedNda {
  const effectiveDate = formatDate(data.effectiveDate);

  const sharedValues: Record<string, string> = {
    purpose: orBlank(data.purpose, "[Purpose not specified]"),
    effectiveDate,
    governingLaw: orBlank(data.governingLaw, "[Governing Law not specified]"),
    jurisdiction: orBlank(data.jurisdiction, "[Jurisdiction not specified]"),
  };

  const coverPage = renderTemplate(COVER_PAGE_TEMPLATE, {
    ...sharedValues,
    mndaTermChecklist: mndaTermChecklist(data),
    confidentialityChecklist: confidentialityChecklist(data),
    modifications: orBlank(data.modifications, "None."),
    party1Name: orBlank(data.partyA.name, "[Party 1 Name]"),
    party1Title: orBlank(data.partyA.title, "[Party 1 Title]"),
    party1Company: orBlank(data.partyA.company, "[Party 1 Company]"),
    party1Address: orBlank(data.partyA.noticeAddress, "[Party 1 Notice Address]"),
    party2Name: orBlank(data.partyB.name, "[Party 2 Name]"),
    party2Title: orBlank(data.partyB.title, "[Party 2 Title]"),
    party2Company: orBlank(data.partyB.company, "[Party 2 Company]"),
    party2Address: orBlank(data.partyB.noticeAddress, "[Party 2 Notice Address]"),
  });

  const standardTerms = renderTemplate(STANDARD_TERMS_TEMPLATE, {
    ...sharedValues,
    mndaTermPhrase: mndaTermPhrase(data),
    confidentialityTermPhrase: confidentialityTermPhrase(data),
  });

  return { coverPage, standardTerms, full: `${coverPage}\n---\n\n${standardTerms}` };
}
