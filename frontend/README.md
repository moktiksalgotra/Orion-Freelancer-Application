# Upwork Job Analyzer - React Frontend

A modern React frontend for the Upwork Job Analyzer application, built with Vite, Tailwind CSS, and modern JavaScript.

## 🚀 Features

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Tailwind CSS**: Modern, utility-first CSS framework
- **Dark/Light Mode**: Clean, professional interface
- **Real-time Updates**: Live backend status indicator

### 📱 Pages & Components
- **Dashboard**: Overview with statistics and quick actions
- **Profiles**: CRUD operations for freelancer profiles
- **Job Scraping**: Keyword-based job scraping interface
- **Job Analysis**: Job fit analysis and recommendations
- **Proposals**: AI-powered proposal generation
- **Analytics**: Performance metrics and insights

### 🔧 Technical Features
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Heroicons**: Beautiful, consistent icons
- **Headless UI**: Accessible UI components
- **Responsive Layout**: Mobile-first design

## 🛠️ Tech Stack

- **React 19**: Latest React with hooks and modern patterns
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API requests
- **Heroicons**: Icon library
- **Headless UI**: Accessible UI components

## 📦 Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Visit `http://localhost:5173`

## 🔌 Backend Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`. Make sure the backend is running before using the frontend.

### API Endpoints Used:
- `GET /api/v1/profiles/` - Get all profiles
- `POST /api/v1/profiles/` - Create profile
- `PUT /api/v1/profiles/{id}` - Update profile
- `DELETE /api/v1/profiles/{id}` - Delete profile
- `POST /api/v1/jobs/scrape` - Scrape jobs
- `GET /api/v1/jobs/scraped` - Get scraped jobs
- `POST /api/v1/jobs/analyze` - Analyze job
- `POST /api/v1/proposals/generate` - Generate proposal
- `GET /api/v1/analytics/dashboard` - Get dashboard stats

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable components
│   │   └── layout/        # Layout components (Navbar, Sidebar)
│   │   └── pages/         # Page components
│   │   └── services/      # API services
│   │   └── App.jsx        # Main app component
│   │   └── main.jsx       # App entry point
│   │   └── index.css      # Global styles
│   ├── package.json
│   ├── tailwind.config.js  # Tailwind configuration
│   ├── postcss.config.js   # PostCSS configuration
│   └── vite.config.js      # Vite configuration
```

## 🎨 Styling

The app uses Tailwind CSS with custom components:

### Custom Classes:
- `.btn-primary` - Primary button style
- `.btn-secondary` - Secondary button style
- `.btn-success` - Success button style
- `.btn-warning` - Warning button style
- `.btn-danger` - Danger button style
- `.card` - Card container style
- `.input-field` - Input field style
- `.textarea-field` - Textarea field style
- `.select-field` - Select field style

### Color Scheme:
- **Primary**: Blue shades for main actions
- **Success**: Green shades for positive actions
- **Warning**: Yellow/Orange shades for warnings
- **Danger**: Red shades for destructive actions

## 🚀 Development

### Available Scripts:
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Development Tips:
1. **Hot Reload**: Changes are reflected immediately
2. **Backend Status**: Check the status indicator in the navbar
3. **Responsive Design**: Test on different screen sizes
4. **Browser DevTools**: Use React DevTools for debugging

## 🔧 Configuration

### Environment Variables:
Create a `.env` file in the frontend directory:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Tailwind Configuration:
Custom colors and fonts are defined in `tailwind.config.js`:
- Custom color palette for primary, success, warning, danger
- Inter font family
- Responsive breakpoints

## 📱 Responsive Design

The app is fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Features:
- Collapsible sidebar
- Touch-friendly buttons
- Optimized forms
- Mobile navigation

## 🎯 Features Status

### ✅ Completed:
- [x] Project setup with Vite + React
- [x] Tailwind CSS configuration
- [x] Routing with React Router
- [x] API service layer
- [x] Layout components (Navbar, Sidebar)
- [x] Dashboard page
- [x] Profiles management
- [x] Basic page structure

### 🚧 In Progress:
- [ ] Job scraping interface
- [ ] Job analysis interface
- [ ] Proposal generation interface
- [ ] Analytics dashboard
- [ ] Real-time data updates

### 📋 Planned:
- [ ] Advanced filtering
- [ ] Export functionality
- [ ] Dark mode toggle
- [ ] Notifications
- [ ] Offline support

## 🐛 Troubleshooting

### Common Issues:

1. **Backend Connection Failed**
   - Ensure the FastAPI backend is running on port 8000
   - Check the backend status indicator in the navbar

2. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for syntax errors in components

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check that PostCSS is working

4. **API Errors**
   - Check browser console for error messages
   - Verify API endpoints are correct
   - Ensure CORS is configured on the backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy coding! 🚀**
