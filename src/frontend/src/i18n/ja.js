// ---- UI strings, Japanese (externalized per the Unit 1 design decision) ----
// All user-facing text lives here so the interface language can be swapped
// without touching component logic (Japanese-first, i18n-ready).

export const ja = {
  appTitle: 'こころの健康チェック',
  appSubtitle: 'さびしさの気持ちを、ときどき確かめるための道具です',

  // Login / registration
  login: 'ログイン',
  register: 'はじめて使う（登録）',
  username: 'ユーザー名',
  password: 'パスワード（8文字以上）',
  displayName: 'お名前（表示用）',
  roleLabel: 'どちらですか？',
  roleOlderAdult: '本人（チェックを受ける方）',
  roleCaregiver: '見守る方（家族・支援者）',
  loginButton: 'ログインする',
  registerButton: '登録する',
  switchToRegister: '登録がまだの方はこちら',
  switchToLogin: 'ログインはこちら',
  logout: 'ログアウト',

  // Consent (M2)
  consentTitle: 'はじめに、ご同意ください',
  consentBody:
    'このアプリは、あなたの「さびしさ」についての3つの質問への答えと、' +
    'その点数の変化を記録します。記録は、あなたが許可した見守りの方だけが' +
    '見ることができます。この記録は病気の診断ではありません。' +
    '同意は、いつでも設定から取り消すことができます。',
  consentAgree: '同意して始める',
  consentRevoke: '同意を取り消す',
  consentRevoked: '同意を取り消しました。記録は見守りの方から見えなくなりました。',

  // Questionnaire (M3) — Three-Item Loneliness Scale (Hughes et al., 2004)
  questionnaireTitle: 'きょうの3つの質問',
  questionnaireLead: '最近のお気持ちに、いちばん近いものを選んでください。',
  q1: '自分には人とのつきあいが足りない、と感じることがありますか？',
  q2: '取り残されている、と感じることがありますか？',
  q3: 'まわりから孤立している、と感じることがありますか？',
  answer1: 'ほとんどない',
  answer2: 'ときどきある',
  answer3: 'よくある',
  submitAnswers: 'こたえを送る',
  answerAllItems: '3つの質問すべてにお答えください。',

  // Dashboard (M7)
  dashboardTitle: 'これまでの記録',
  latestScore: '今回の点数',
  scoreRange: '（3〜9点。高いほど、さびしさが強いことを表します）',
  trendLabel: '最近の傾向',
  trendRising: '上がってきています',
  trendFalling: '下がってきています',
  trendStable: '安定しています',
  flagNone: 'いまのところ、心配な傾向はありません。',
  flagSustainedHigh:
    '高めの点数が続いています。信頼できる人と話す機会を持ってみませんか。',
  flagWorsening:
    '点数が上がってきています。信頼できる人と話す機会を持ってみませんか。',
  notDiagnosis: 'これは気持ちのチェックであり、診断ではありません。',
  noRecords: 'まだ記録がありません。きょうの質問に答えてみましょう。',
  answerAgain: 'もう一度こたえる',

  // Caregiver view
  caregiverTitle: '見守りのページ',
  caregiverLead: '同意をいただいている方の記録だけが表示されます。',
  linkPlaceholder: '見守りたい方のユーザー名',
  linkButton: '見守りに追加',
  noLinkedPeople: 'まだ見守っている方がいません。',
  lastScoreLabel: '最新の点数',
  attentionLabel: '注意',
  attentionNeeded: '気にかけてあげてください',
  noAttention: '心配な傾向はありません',

  // Errors
  errorGeneric: 'うまくいきませんでした。もう一度お試しください。',
  errorLogin: 'ユーザー名またはパスワードが違います。',
}
