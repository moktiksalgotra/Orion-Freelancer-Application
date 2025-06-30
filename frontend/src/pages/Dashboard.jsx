import { Link } from 'react-router-dom';
import {
  ArrowRightIcon,
  UserIcon,
  SparklesIcon,
  RocketLaunchIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline';
import upworkLogo from '../assets/upwork.svg';
import freelancerImage from '../assets/freelancer.png';

// Simple reusable Card component
const FeatureCard = ({ icon, title, description }) => (
    <div className="flex flex-col items-start gap-3 p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
        {icon}
        <h3 className="text-lg font-semibold text-gray-900">
            {title}
        </h3>
        <p className="text-sm text-gray-600 flex-1">{description}</p>
    </div>
);

const Dashboard = () => {
    // Feature data for cards
    const features = [
        {
            title: 'Scrape Jobs',
            description: 'Find and collect relevant job opportunities from Upwork.',
            icon: <RocketLaunchIcon className="w-8 h-8 text-blue-600" />,
        },
        {
            title: 'Analyze Jobs',
            description: 'Get AI-powered insights and recommendations for scraped jobs.',
            icon: <CpuChipIcon className="w-8 h-8 text-green-600" />,
        },
        {
            title: 'Generate Proposals',
            description: 'Create personalized, winning proposals in seconds.',
            icon: <SparklesIcon className="w-8 h-8 text-purple-600" />,
        },
        {
            title: 'Manage Profiles',
            description: 'Optimize your freelancer profiles to attract more clients.',
            icon: <UserIcon className="w-8 h-8 text-orange-600" />,
        },
    ];

    return (
        <div className="bg-gray-50 min-h-screen p-8 mt-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-12">
                    <div className="text-left">
                        <h1 className="text-4xl lg:text-5xl font-bold text-gray-800 tracking-tight">
                            Empower Your Freelance Career with<br />
                            <span className="bg-gradient-to-r from-orange-400 to-blue-500 bg-clip-text text-transparent">
                                AI-Powered
                            </span>
                            <span> Job Intelligence</span>
                        </h1>
                        <p className="mt-4 text-lg text-gray-600 max-w-3xl">
                            Automated job scraping, AI-driven analysis, and instant proposal generation to streamline your Upwork workflow.
                        </p>
                        <div className="mt-8">
                            <Link
                                to="/job-scraping"
                                className="inline-flex items-center px-6 py-3 bg-gray-900 text-white font-semibold rounded-full shadow-md hover:bg-gray-800 transition-transform transform hover:-translate-y-1"
                            >
                                <span>Get Started</span>
                                <ArrowRightIcon className="w-5 h-5 ml-2" />
                            </Link>
                        </div>
                    </div>
                    {/* Hero illustration */}
                    <div className="hidden lg:block">
                        <img src={freelancerImage} alt="Freelancer working" className="h-64 w-auto" />
                    </div>
                </div>

                {/* Bullet-list feature section (new layout) */}
                <div className="my-16 lg:grid lg:grid-cols-12 lg:gap-12 items-center">
                    {/* Left column: heading & bullets */}
                    <div className="lg:col-span-6 order-2 lg:order-2">
                            
                        <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                             <span>Core Features</span>
                        </h2>

                        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-6">
                            {features.map((feature) => (
                                <FeatureCard key={feature.title} {...feature} />
                            ))}
                        </div>
                    </div>

                    {/* Right column: call-to-action banner */}
                    <div className="lg:col-span-6 mb-8 lg:mb-0 order-1 lg:order-1">
                        <div className="w-full h-64 bg-gray-900 text-white rounded-2xl p-10 flex items-center justify-center shadow-lg">
                            <h3 className="text-3xl sm:text-4xl font-extrabold leading-tight text-center">
                            Let's supercharge your Upwork workflow together. 
                            </h3>
                        </div>
                    </div>
                </div>

                {/* Informational Card */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                   <div className="flex items-center">
                    <img src={upworkLogo} alt="Upwork Logo" className="w-24 h-auto object-contain mr-6" />
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800">Automate Your Upwork Journey</h3>
                        <p className="text-gray-600 mt-1">This application leverages automation and AI to streamline your Upwork workflow, from finding jobs to generating proposals. Focus on what matters: winning projects.</p>
                    </div>
                   </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard; 