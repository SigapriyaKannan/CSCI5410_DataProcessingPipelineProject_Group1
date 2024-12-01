"use client";

import { useContext, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { auth_api, log_api, login_success_email } from "@/lib/constants";
import { toast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { UserContext } from "../contexts/user-context";

export default function LoginPage() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [securityQuestion, setSecurityQuestion] = useState("");
  const [securityAnswer, setSecurityAnswer] = useState("");
  const [actualSecurityAnswer, setActualSecurityAnswer] = useState("");
  const [idToken, setIdToken] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [mathAnswer, setMathAnswer] = useState("");
  const [mathOperand1, setMathOperand1] = useState(0);
  const [mathOperand2, setMathOperand2] = useState(0);
  const [operand, setOperand] = useState("");
  const [answerToBe, setAnswerToBe] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { setUser } = useContext(UserContext);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (step === 1) {
        console.log("Authenticating with Cognito:", email, password);
        const response = await fetch(`${auth_api}/api/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        });

        const result = await response.json();

        if (result?.status !== "Success") {
          setError(result.error || "Login failed.");
          setLoading(false);
          toast({
            title: "Login failed",
            description: result?.message,
          });
          return;
        }

        setSecurityQuestion(result?.securityQuestion);
        setActualSecurityAnswer(result?.securityAnswer);

        setIdToken(result?.idToken);
        setAccessToken(result?.AccessToken);
        setRole(result?.role);

        const mathResponse = await fetch(`${auth_api}/api/mathskill`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email: email }),
        });

        if (result?.status !== "Success") {
          const result = await mathResponse.json();
          setError(result.error || "Failed to retrieve math question.");
          setLoading(false);
          return;
        }

        const mathResult = await mathResponse.json();
        setMathOperand1(mathResult.operands[0]);
        setMathOperand2(mathResult.operands[1]);
        setAnswerToBe(mathResult.answer);

        switch (mathResult.operand) {
          case "addition":
            setOperand("+");
            break;
          case "subtraction":
            setOperand("-");
            break;
          default:
            setOperand("=");
            break;
        }
        toast({
          title: "Success",
          description: "Please continue with security questions now",
        });
        setLoading(false);
        setStep(2);
      } else if (step === 2) {
        console.log("Checking security answer:", securityAnswer);
        if (securityAnswer !== actualSecurityAnswer) {
          setError("Wrong Answer");
          setLoading(false);
          toast({
            title: "Login failed",
            description: "Please give the correct answer to continue",
          });
          return;
        }

        toast({
          title: "Success",
          description: "Please continue with Math question now",
        });
        setLoading(false);
        setStep(3);
      } else if (step === 3) {
        console.log("Checking math answer:", mathAnswer);

        if (parseInt(mathAnswer) !== answerToBe) {
          setError("Incorrect answer. Please try again.");
          setLoading(false);
          toast({
            title: "Wrong Answer",
            description: "Please try again",
          });
          return;
        }

        const login_success_response = await fetch(`${auth_api}/api/sns`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            subject: login_success_email.subject,
            message: login_success_email.message,
          }),
        });

        const log_user_login_response = await fetch(
          `${log_api}/log-user-login`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              user_id: email,
              user_type: role,
            }),
          },
        );

        setUser({
          email: email,
          idToken: idToken,
          accessToken: accessToken,
          role: role,
        });

        toast({
          title: "Correct! Login Success",
          description: "Redirecting to Homepage",
        });
        setLoading(false);
        router.replace("/");
      }
    } catch (err) {
      console.error(err);
      setError("Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <Card className="w-[350px]">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>
            {step === 1 && "Enter your credentials"}
            {step === 2 && "Answer your security question"}
            {step === 3 && "Solve the math problem"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            {step === 1 && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}
            {step === 2 && (
              <div className="space-y-2">
                <Label htmlFor="security-answer">{securityQuestion}</Label>
                <Input
                  id="security-answer"
                  type="text"
                  value={securityAnswer}
                  onChange={(e) => setSecurityAnswer(e.target.value)}
                  required
                />
              </div>
            )}
            {step === 3 && (
              <div className="space-y-2">
                <Label htmlFor="math-answer">
                  {`What is ${mathOperand1} ${operand} ${mathOperand2}?`}
                </Label>
                <Input
                  id="math-answer"
                  type="number"
                  value={mathAnswer}
                  onChange={(e) => setMathAnswer(e.target.value)}
                  required
                />
              </div>
            )}
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            <Button type="submit" className="w-full mt-4" disabled={loading}>
              {loading ? "Processing..." : step === 3 ? "Login" : "Next"}
            </Button>
          </form>
        </CardContent>
        <CardFooter>
          <p className="text-sm text-gray-500">
            Don&apos;t have an account?{" "}
            <a href="/signup" className="text-blue-500 hover:underline">
              Sign up
            </a>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
