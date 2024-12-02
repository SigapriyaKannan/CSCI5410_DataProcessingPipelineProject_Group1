"use client";

import { useState } from "react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  auth_api,
  register_started_email,
  register_success_email,
} from "@/lib/constants";
import { security_questions_type, signup_request_type } from "../types/auth";
import { useRouter } from "next/navigation";
import { toast } from "@/hooks/use-toast";

export default function SignupPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    role: "",
    securityQuestion1: "",
    securityAnswer1: "",
    securityQuestion2: "",
    securityAnswer2: "",
    mathAnswer: "",
  });
  const [mathOperand1, setMathOperand1] = useState(0);
  const [mathOperand2, setMathOperand2] = useState(0);
  const [operand, setOperand] = useState("");
  const [answerToBe, setAnswerToBe] = useState(0);
  const [error, setError] = useState("");

  const router = useRouter();

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement> | string,
    name?: string,
  ) => {
    if (typeof e === "string" && name) {
      setFormData((prevData) => ({ ...prevData, [name]: e }));
    } else if (typeof e !== "string") {
      const target = e.target as HTMLInputElement;
      setFormData((prevData) => ({ ...prevData, [target.name]: target.value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (step === 1) {
        if (formData.password !== formData.confirmPassword) {
          setError("Passwords do not match.");
          setLoading(false);
          return;
        }
        if (
          formData.role !== "Registered" &&
          formData.role !== "Agent" &&
          formData.role !== "Guest"
        ) {
          setError("Please choose a correct role.");
          setLoading(false);
          return;
        }

        const signupRequestData: signup_request_type = {
          email: formData.email,
          password: formData.password,
          role: formData.role,
        };

        const response = await fetch(`${auth_api}/api/signup`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(signupRequestData),
        });

        const result = await response.json();
        if (result?.status !== "Success") {
          setError(result.error || "Signup failed.");
          setLoading(false);
          toast({
            title: "Signup failed",
            description: result?.message,
          });
          return;
        }

        const register_started_response = await fetch(`${auth_api}/api/sns`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: formData.email,
            subject: register_started_email.subject,
            message: register_started_email.message,
          }),
        });

        toast({
          title: "Registration success",
          description: "Make sure to remember the password",
        });
        setStep(2);
      } else if (step === 2) {
        const securityQuestionsRequestData: security_questions_type = {
          email: formData.email,
          securityQuestion1: formData.securityQuestion1,
          securityAnswer1: formData.securityAnswer1,
          securityQuestion2: formData.securityQuestion2,
          securityAnswer2: formData.securityAnswer2,
        };

        const response = await fetch(
          `${auth_api}/api/signup/securityquestions`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(securityQuestionsRequestData),
          },
        );

        const result = await response.json();
        if (result?.status !== "Success") {
          setError(result.error || "Failed to save security questions.");
          setLoading(false);
          toast({
            title: "Security Question setup failed",
            description: result?.message,
          });
          return;
        }

        const mathResponse = await fetch(`${auth_api}/api/mathskill`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email: formData.email }),
        });

        const mathResult = await mathResponse.json();
        if (mathResult?.status !== "Success") {
          setError(mathResult.error || "Failed to retrieve math question.");
          setLoading(false);
          return;
        }

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
          title: "Security Question setup success",
          description: "All questions were set",
        });
        setStep(3);
      } else if (step === 3) {
        if (parseInt(formData.mathAnswer) !== answerToBe) {
          setError("Incorrect answer. Please try again.");
          setLoading(false);
          toast({
            title: "Wrong Answer",
            description: "Please try again",
          });
          return;
        }

        const response = await fetch(`${auth_api}/api/signup/confirmation`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: formData.email,
            status: "Confirmed",
          }),
        });

        const result = await response.json();
        if (result?.status !== "Success") {
          setError(result.error || "Signup confirmation failed.");
          setLoading(false);
          toast({
            title: "Signup confirmation failed",
            description: result?.message,
          });
          return;
        }

        const register_success_response = await fetch(`${auth_api}/api/sns`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: formData.email,
            subject: register_success_email.subject,
            message: register_success_email.message,
          }),
        });

        toast({
          title: "Signup successful",
        });
        router.push("/login");
      }
    } catch (err) {
      console.error(err);
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <Card className="w-[400px]">
        <CardHeader>
          <CardTitle>Sign Up</CardTitle>
          <CardDescription>
            {step === 1 && "Create your account"}
            {step === 2 && "Set up your security questions"}
            {step === 3 && "Verify your math skills"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            {step === 1 && (
              <div className="space-y-2">
                <div className="space-y-1">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="role">Role</Label>
                  <Select
                    onValueChange={(value) => handleChange(value, "role")}
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Agent">Agent</SelectItem>
                      <SelectItem value="Registered">User</SelectItem>
                      <SelectItem value="Guest">Guest</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            )}
            {step === 2 && (
              <div className="space-y-4">
                <div className="space-y-1">
                  <Label htmlFor="securityQuestion1">Security Question 1</Label>
                  <Input
                    id="securityQuestion1"
                    name="securityQuestion1"
                    type="text"
                    value={formData.securityQuestion1}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="securityAnswer1">Answer 1</Label>
                  <Input
                    id="securityAnswer1"
                    name="securityAnswer1"
                    type="text"
                    value={formData.securityAnswer1}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="securityQuestion2">Security Question 2</Label>
                  <Input
                    id="securityQuestion2"
                    name="securityQuestion2"
                    type="text"
                    value={formData.securityQuestion2}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="securityAnswer2">Answer 2</Label>
                  <Input
                    id="securityAnswer2"
                    name="securityAnswer2"
                    type="text"
                    value={formData.securityAnswer2}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            )}
            {step === 3 && (
              <div className="space-y-1">
                <Label htmlFor="mathAnswer">
                  {`What is ${mathOperand1} ${operand} ${mathOperand2}?`}
                </Label>
                <Input
                  id="mathAnswer"
                  name="mathAnswer"
                  type="number"
                  value={formData.mathAnswer}
                  onChange={handleChange}
                  required
                />
              </div>
            )}
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            <Button type="submit" className="w-full mt-4" disabled={loading}>
              {loading ? "Processing..." : step === 3 ? "Sign Up" : "Next"}
            </Button>
          </form>
        </CardContent>
        <CardFooter>
          <p className="text-sm text-gray-500">
            Already have an account?{" "}
            <a href="/login" className="text-blue-500 hover:underline">
              Log in
            </a>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
