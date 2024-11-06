export type signup_request_type = {
  email: string;
  password: string;
  role: "Agent" | "Registered" | "Guest";
};

export type security_questions_type = {
  email: string;
  securityQuestion1: string;
  securityAnswer1: string;
  securityQuestion2: string;
  securityAnswer2: string;
};
