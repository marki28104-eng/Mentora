
import { NavLink } from 'react-router-dom';
import './Navigation.css';

const Navigation = ({
        items = [],
        variant = 'horizontal',
        className = '',
        ...props
}) => {
        const getNavClasses = () => {
                const baseClasses = 'nav-modern glass-nav';
                const variantClasses = {
                        horizontal: 'nav-horizontal',
                        vertical: 'nav-vertical',
                        sidebar: 'nav-sidebar'
                };

                return `${baseClasses} ${variantClasses[variant]} ${className}`;
        };

        return (
                <nav className={getNavClasses()} {...props}>
                        <div className="nav-container">
                                {items.map((item, index) => (
                                        <NavigationItem
                                                key={item.key || index}
                                                item={item}
                                                variant={variant}
                                        />
                                ))}
                        </div>
                </nav>
        );
};

const NavigationItem = ({ item }) => {
        const {
                to,
                href,
                label,
                icon,
                badge,
                disabled = false,
                onClick,
                children
        } = item;

        const getItemClasses = () => {
                const baseClasses = 'nav-item transition-smooth focus-purple';
                const disabledClass = disabled ? 'nav-item-disabled' : '';
                return `${baseClasses} ${disabledClass}`;
        };

        const renderContent = () => (
                <>
                        {icon && <span className="nav-item-icon">{icon}</span>}
                        <span className="nav-item-label">{label}</span>
                        {badge && <span className="nav-item-badge">{badge}</span>}
                </>
        );

        if (disabled) {
                return (
                        <span className={getItemClasses()}>
                                {renderContent()}
                        </span>
                );
        }

        if (to) {
                return (
                        <NavLink
                                to={to}
                                className={({ isActive }) =>
                                        `${getItemClasses()} ${isActive ? 'nav-item-active' : ''}`
                                }
                                onClick={onClick}
                        >
                                {renderContent()}
                                {children}
                        </NavLink>
                );
        }

        if (href) {
                return (
                        <a
                                href={href}
                                className={getItemClasses()}
                                onClick={onClick}
                                target="_blank"
                                rel="noopener noreferrer"
                        >
                                {renderContent()}
                                {children}
                        </a>
                );
        }

        return (
                <button
                        className={getItemClasses()}
                        onClick={onClick}
                        type="button"
                >
                        {renderContent()}
                        {children}
                </button>
        );
};

// Breadcrumb Navigation Component
const Breadcrumb = ({ items = [], separator = '/', className = '' }) => {
        return (
                <nav className={`breadcrumb-nav ${className}`} aria-label="Breadcrumb">
                        <ol className="breadcrumb-list">
                                {items.map((item, index) => (
                                        <li key={item.key || index} className="breadcrumb-item">
                                                {index > 0 && <span className="breadcrumb-separator">{separator}</span>}
                                                {item.to ? (
                                                        <NavLink
                                                                to={item.to}
                                                                className="breadcrumb-link"
                                                        >
                                                                {item.label}
                                                        </NavLink>
                                                ) : (
                                                        <span className="breadcrumb-current">{item.label}</span>
                                                )}
                                        </li>
                                ))}
                        </ol>
                </nav>
        );
};

// Tab Navigation Component
const TabNavigation = ({
        tabs = [],
        activeTab,
        onTabChange,
        className = ''
}) => {
        return (
                <div className={`tab-nav ${className}`}>
                        <div className="tab-list" role="tablist">
                                {tabs.map((tab) => (
                                        <button
                                                key={tab.key}
                                                role="tab"
                                                aria-selected={activeTab === tab.key}
                                                className={`tab-item ${activeTab === tab.key ? 'tab-active' : ''}`}
                                                onClick={() => onTabChange(tab.key)}
                                        >
                                                {tab.icon && <span className="tab-icon">{tab.icon}</span>}
                                                <span className="tab-label">{tab.label}</span>
                                                {tab.badge && <span className="tab-badge">{tab.badge}</span>}
                                        </button>
                                ))}
                        </div>
                </div>
        );
};

export { Navigation, Breadcrumb, TabNavigation };
export default Navigation;