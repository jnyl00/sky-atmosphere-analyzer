import { Route, Routes } from "react-router-dom";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { UploadPage, ResultsPage } from "@/routes";

export default function App() {
    return (
        <Routes>
            <Route
                path="/"
                element={
                        <DashboardLayout>
                            <UploadPage />
                        </DashboardLayout>
                }
            />
            <Route
                path="/results"
                element={
                        <DashboardLayout>
                            <ResultsPage />
                        </DashboardLayout>
                }
            />
        </Routes>
    );
}
