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
import { auth_api } from "@/lib/constants";
import { security_questions_type, signup_request_type } from "../types/auth";
import { redirect, useRouter } from "next/navigation";

export default function SignupPage() {
  const [step, setStep] = useState(1);
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
  const [operand, setOperand] = useState("/");
  const [answerToBe, setAnswerToBe] = useState(-1);
  const [error, setError] = useState("");

  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (value: string) => {
    setFormData({ ...formData, role: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      if (step === 1) {
        if (formData.password !== formData.confirmPassword) {
          setError("Passwords do not match");
          return;
        }
        if (formData.role !== "Agent" && formData.role !== "Registered") {
          setError("Please choose a correct role");
          return;
        }
        // TODO: Implement AWS Cognito user creation
        console.log(
          "Creating user with api:",
          formData.email,
          formData.role,
          formData.password,
        );

        try {
          const signupRequestData: signup_request_type = {
            email: formData.email,
            password: formData.password,
            role: formData.role,
          };

          const response = await fetch(auth_api + "/api/signup", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(signupRequestData),
          });

          const result = await response.json();

          if (result?.status === "Success") {
            console.log("signup success", result);
            setError("");
            setStep(2);
          } else {
            console.log("signup fail", result);
            setError(result.error || "Signup failed.");
          }
        } catch (err) {
          setError("An error occurred. Please try again.");
        }
      } else if (step === 2) {
        // TODO: Implement DynamoDB security question storage
        console.log(
          formData.email,
          formData.securityQuestion1,
          formData.securityAnswer1,
          formData.securityQuestion2,
          formData.securityAnswer2,
        );

        try {
          const securityQuestionsRequestData: security_questions_type = {
            email: formData.email,
            securityQuestion1: formData.securityQuestion1,
            securityAnswer1: formData.securityAnswer1,
            securityQuestion2: formData.securityQuestion2,
            securityAnswer2: formData.securityAnswer2,
          };

          const response = await fetch(
            auth_api + "/api/signup/securityquestions",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(securityQuestionsRequestData),
            },
          );

          const result = await response.json();

          if (result?.status === "Success") {
            console.log("signup success", result);
            setError("");
            try {
              const math_response = await fetch(auth_api + "/api/mathskill", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({ email: formData.email }),
              });

              const math_result = await math_response.json();

              if (math_result?.status === "Success") {
                setMathOperand1(math_result.operands[0]);
                setMathOperand2(math_result.operands[1]);
                setAnswerToBe(math_result.answer);

                if (math_result.operand === "addition") {
                  setOperand("+");
                } else if (math_result.operand === "subtraction") {
                  setOperand("-");
                } else {
                  setOperand("=");
                }
                console.log("have set the math skill inputs");
              }
            } catch (err) {
              setError("An error occurred. Please try again.");
            }
            setStep(3);
          } else {
            console.log("signup fail", result);
            setError(result.error || "Signup failed.");
          }
        } catch (err) {
          setError("An error occurred. Please try again.");
        }
      } else if (step === 3) {
        // TODO: Implement Lambda math skills verification
        console.log("Verifying math skills:", formData.mathAnswer);
        if (parseInt(formData.mathAnswer) === answerToBe) {
          console.log("Correct answer. now confirming");

          try {
            const response = await fetch(
              auth_api + "/api/signup/confirmation",
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  email: formData.email,
                  status: "Confirmed",
                }),
              },
            );

            const result = await response.json();

            if (result?.status === "Success") {
              console.log("signup success", result);
              setError("");
              router.replace("/");
            } else {
              console.log("signup fail", result);
              setError(result.error || "Signup failed.");
            }
          } catch (err) {
            console.log(err);
            setError("An error occurred. Please try again.");
          }
        }
      }
    } catch (err) {
      setError("Signup failed. Please try again.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <Card className="w-[400px]">
        <CardHeader>
          <CardTitle>Sign Up</CardTitle>
          <CardDescription>
            {step === 1 && "Create your account"}
            {step === 2 && "Set up your security question"}
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
                  <Select onValueChange={handleSelectChange}>
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
                  {`What is ${mathOperand1} ${operand} ${mathOperand2}`}
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
            <Button type="submit" className="w-full mt-4">
              {step === 3 ? "Sign Up" : "Next"}
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
