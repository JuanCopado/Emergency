/** Local label screen only; backend screening and manual privacy review remain required. */
const directIdentifierLabel = /\b(nome(?: completo| do paciente| do doente)?|name|patient(?: name)?|nombre(?: completo| del paciente)?|paciente|doente|sns|nif|nhs|mrn|dni|nie|processo|historia cl[ií]nica|n[uú]mero de historia|passport|pasaporte|morada|endere[cç]o|address|direcci[oó]n|domicilio|telefone|telem[oó]vel|phone|telephone|tel[eé]fono|m[oó]vil)\b\s*[:：-]|(?:姓名|患者姓名|病人姓名|患者|病人|地址|住址|电话|電話|手机|手機|身份证|身份證|病历号|病歷號|护照|護照)\s*[:：-]/i;

export function hasLocalIdentifierLabel(value: string): boolean {
  return directIdentifierLabel.test(value);
}
