"use client";

import React, { useContext } from "react";
import { UserContext } from "@/app/contexts/user-context";

const DashboardPage = () => {
  const { user } = useContext(UserContext);

  const lookerStudioUrl =
    "https://lookerstudio.google.com/embed/reporting/bd5329ea-69c6-4e1e-9135-bd0e26aca42b/page/OTOXE";

  console.log(user);
  
  if (!user || user.role !== "Agent") {
    return <div>You are not authorized to access this page.</div>;
  }

  return (
    <div className="flex align-middle justify-center h-[80vh] w-full border bottom-1">
      <iframe
        className="w-full"
        src={lookerStudioUrl}
        allowFullScreen
        title="Looker Studio Report"
      ></iframe>
    </div>
  );
};

export default DashboardPage;
