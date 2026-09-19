export interface PartyInfo {
  name: string;
  title: string;
  company: string;
  noticeAddress: string;
}

export type MndaTermType = "fixed" | "until-terminated";
export type ConfidentialityTermType = "fixed" | "perpetuity";

export interface NdaFormData {
  purpose: string;
  effectiveDate: string;
  termType: MndaTermType;
  termYears: number;
  confidentialityType: ConfidentialityTermType;
  confidentialityYears: number;
  governingLaw: string;
  jurisdiction: string;
  modifications: string;
  partyA: PartyInfo;
  partyB: PartyInfo;
}

export const emptyParty = (): PartyInfo => ({
  name: "",
  title: "",
  company: "",
  noticeAddress: "",
});

export const defaultNdaFormData = (): NdaFormData => ({
  purpose: "Evaluating whether to enter into a business relationship with the other party.",
  effectiveDate: new Date().toISOString().slice(0, 10),
  termType: "fixed",
  termYears: 1,
  confidentialityType: "fixed",
  confidentialityYears: 1,
  governingLaw: "",
  jurisdiction: "",
  modifications: "",
  partyA: emptyParty(),
  partyB: emptyParty(),
});
