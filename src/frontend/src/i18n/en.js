// ---- UI strings, English ----
// English mirror of ja.js. The default language for coursework evaluation;
// the interface ships Japanese-first for end users (Unit 1 design decision)
// and the externalized strings make the swap a one-line change.

export const en = {
  appTitle: 'Loneliness Check',
  appSubtitle: 'A simple tool to check in on feelings of loneliness',

  // Login / registration
  login: 'Log in',
  register: 'First time here (register)',
  username: 'Username',
  password: 'Password (8 or more characters)',
  displayName: 'Your name (shown on screen)',
  roleLabel: 'Which describes you?',
  roleOlderAdult: 'I am taking the check myself',
  roleCaregiver: 'I support someone (family or caregiver)',
  loginButton: 'Log in',
  registerButton: 'Register',
  switchToRegister: 'Not registered yet? Start here',
  switchToLogin: 'Already registered? Log in here',
  logout: 'Log out',

  // Consent (M2)
  consentTitle: 'Before you start, please give your consent',
  consentBody:
    'This app records your answers to three questions about loneliness ' +
    'and how your score changes over time. Only the supporters you ' +
    'authorize can see your records. This is a screening aid, not a ' +
    'medical diagnosis. You can withdraw your consent at any time from ' +
    'the settings.',
  consentAgree: 'I agree, start',
  consentRevoke: 'Withdraw consent',
  consentRevoked:
    'Your consent has been withdrawn. Your records are no longer visible ' +
    'to your supporters.',

  // Questionnaire (M3) — Three-Item Loneliness Scale (Hughes et al., 2004)
  questionnaireTitle: "Today's three questions",
  questionnaireLead: 'Choose the answer closest to how you have been feeling.',
  q1: 'How often do you feel that you lack companionship?',
  q2: 'How often do you feel left out?',
  q3: 'How often do you feel isolated from others?',
  answer1: 'Hardly ever',
  answer2: 'Some of the time',
  answer3: 'Often',
  submitAnswers: 'Send my answers',
  answerAllItems: 'Please answer all three questions.',

  // Dashboard (M7)
  dashboardTitle: 'Your records',
  latestScore: 'Score this time',
  scoreRange: '(3 to 9. Higher means stronger loneliness.)',
  trendLabel: 'Recent trend',
  trendRising: 'going up',
  trendFalling: 'going down',
  trendStable: 'stable',
  flagNone: 'No worrying pattern so far.',
  flagSustainedHigh:
    'Your score has stayed high. How about finding a moment to talk ' +
    'with someone you trust?',
  flagWorsening:
    'Your score has been going up. How about finding a moment to talk ' +
    'with someone you trust?',
  notDiagnosis: 'This is a check on feelings, not a medical diagnosis.',
  noRecords: "No records yet. Try answering today's questions.",
  answerAgain: 'Answer again',

  // Caregiver view
  caregiverTitle: 'Supporter page',
  caregiverLead: 'Only people with active consent are shown here.',
  linkPlaceholder: 'Username of the person you support',
  linkButton: 'Add to my list',
  noLinkedPeople: 'You are not supporting anyone yet.',
  lastScoreLabel: 'Latest score',
  attentionLabel: 'Attention',
  attentionNeeded: 'please check in with them',
  noAttention: 'no worrying pattern',

  // Errors
  errorGeneric: 'Something went wrong. Please try again.',
  errorLogin: 'The username or password is not correct.',
}
