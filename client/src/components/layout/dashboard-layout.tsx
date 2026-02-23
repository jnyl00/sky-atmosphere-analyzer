import { useState, type ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { Book, Menu, MessageSquare } from "lucide-react";

type DashboardLayoutProps = {
    children: ReactNode;
};

type NavigationItem = {
    name: string;
    href: string;
    icon: typeof Book;
};

const navigation: NavigationItem[] = [
    { name: "Upload", href: "/", icon: Book },
    { name: "Results", href: "/results", icon: MessageSquare },
];

export default function DashboardLayout({ children }: DashboardLayoutProps) {
    const { pathname } = useLocation();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <div className="min-h-screen bg-background">
            <div className="lg:hidden fixed top-0 left-0 m-4 z-50">
                <button
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    className="p-2 rounded-md bg-primary text-primary-foreground"
                    aria-label="Toggle menu"
                >
                    <Menu className="h-6 w-6" />
                </button>
            </div>

            <div
                className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-card border-r transition-transform duration-200 ease-in-out lg:translate-x-0 ${
                    isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
                }`}
            >
                <div className="flex h-full flex-col">
                    <div className="flex h-16 items-center border-b pl-6">
                        <Link
                            to="/"
                            className="flex items-center text-lg font-semibold hover:text-primary transition-colors"
                        >
                            Sky Analyzer
                        </Link>
                    </div>

                    <nav className="flex-1 space-y-2 px-4 py-6">
                        {navigation.map((item) => {
                            const isActive =
                                item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`group flex items-center rounded-lg px-4 py-3 text-sm font-medium transition-all duration-200 ${
                                        isActive
                                            ? "bg-gradient-to-r from-primary/10 to-primary/5 text-primary shadow-sm"
                                            : "text-muted-foreground hover:bg-accent/50 hover:text-foreground hover:shadow-sm"
                                    }`}
                                >
                                    <item.icon
                                        className={`mr-3 h-5 w-5 transition-transform duration-200 ${
                                            isActive
                                                ? "text-primary scale-110"
                                                : "group-hover:scale-110"
                                        }`}
                                    />
                                    <span className="font-medium">
                                        {item.name}
                                    </span>
                                    {isActive && (
                                        <div className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" />
                                    )}
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </div>

            <div className="lg:pl-64">
                <main className="min-h-screen py-6 px-4 sm:px-6 lg:px-8">
                    {children}
                </main>
            </div>
        </div>
    );
}
