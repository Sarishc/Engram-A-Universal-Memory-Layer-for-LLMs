"use client"

import { motion } from "framer-motion"
import { ArrowRight, Brain, Search, Upload, Network, Zap, Shield, Globe, Star, Users, Clock, CheckCircle, Play, Sparkles, Menu, X } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useState } from "react"

const features = [
  {
    icon: Upload,
    title: "Memory Ingestion",
    description: "Upload files, paste text, or connect external sources. Engram processes everything intelligently.",
    color: "from-blue-500 to-cyan-500",
    stats: "10x faster processing"
  },
  {
    icon: Search,
    title: "Semantic Search",
    description: "Find anything instantly with AI-powered search that understands context and meaning.",
    color: "from-purple-500 to-pink-500",
    stats: "Sub-300ms recall"
  },
  {
    icon: Network,
    title: "Knowledge Graph",
    description: "Visualize connections between your memories in an interactive 3D graph.",
    color: "from-green-500 to-emerald-500",
    stats: "Real-time connections"
  },
  {
    icon: Globe,
    title: "Smart Connectors",
    description: "Sync with Google Drive, Notion, Slack, and more. Your knowledge, unified.",
    color: "from-orange-500 to-red-500",
    stats: "50+ integrations"
  }
]

const steps = [
  {
    number: "01",
    title: "Ingest",
    description: "Upload files, paste text, or connect your favorite apps. Engram accepts everything.",
    icon: Upload,
    color: "from-blue-500 to-cyan-500"
  },
  {
    number: "02", 
    title: "Process",
    description: "AI extracts meaning, creates embeddings, and builds connections automatically.",
    icon: Brain,
    color: "from-purple-500 to-pink-500"
  },
  {
    number: "03",
    title: "Recall",
    description: "Search naturally and get instant, relevant results from your entire knowledge base.",
    icon: Search,
    color: "from-green-500 to-emerald-500"
  }
]

const integrations = [
  { name: "Google Drive", logo: "📁", status: "Connected" },
  { name: "Notion", logo: "📝", status: "Connected" },
  { name: "Slack", logo: "💬", status: "Connected" },
  { name: "Chrome", logo: "🌐", status: "Available" },
  { name: "GitHub", logo: "⚡", status: "Available" },
  { name: "Discord", logo: "🎮", status: "Available" }
]

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Product Manager",
    company: "TechCorp",
    content: "Engram transformed how we manage knowledge. 5x faster search, 3x better recall accuracy.",
    avatar: "👩‍💼",
    rating: 5
  },
  {
    name: "Marcus Johnson",
    role: "AI Researcher",
    company: "AI Labs",
    content: "The memory graph visualization is incredible. Finally, we can see how ideas connect.",
    avatar: "👨‍🔬",
    rating: 5
  },
  {
    name: "Elena Rodriguez",
    role: "Content Creator",
    company: "Creative Studio",
    content: "From scattered notes to organized knowledge. Engram made me 10x more productive.",
    avatar: "👩‍🎨",
    rating: 5
  }
]

const pricingPlans = [
  {
    name: "Free",
    price: "$0",
    period: "/month",
    description: "Perfect for getting started with memory as a service.",
    features: [
      "1M tokens processed",
      "10K search queries",
      "Basic connectors",
      "Email support"
    ],
    cta: "Try for free",
    popular: false
  },
  {
    name: "Pro",
    price: "$19",
    period: "/month",
    description: "Memory for power users and quick moving teams.",
    features: [
      "3M tokens processed",
      "100K search queries",
      "All connectors",
      "Priority support",
      "Advanced analytics",
      "Custom integrations"
    ],
    cta: "Get started with Pro",
    popular: true
  },
  {
    name: "Scale",
    price: "$399",
    period: "/month",
    description: "Enterprise-grade memory for large organisations.",
    features: [
      "80M tokens processed",
      "20M search queries",
      "Dedicated support",
      "Custom Integration",
      "Slack Support Channel",
      "SLA guarantee"
    ],
    cta: "Get started with Scale",
    popular: false
  }
]

// Floating particles component
const FloatingParticles = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-white/20 rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -20, 0],
            x: [0, Math.random() * 20 - 10, 0],
            opacity: [0.2, 0.8, 0.2],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}
    </div>
  )
}

// Network graph component
const NetworkGraph = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <svg className="w-full h-full" viewBox="0 0 400 300">
        {[...Array(15)].map((_, i) => (
          <motion.circle
            key={i}
            cx={Math.random() * 400}
            cy={Math.random() * 300}
            r={2 + Math.random() * 3}
            fill="rgba(255, 255, 255, 0.3)"
            animate={{
              opacity: [0.3, 0.8, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
        {[...Array(8)].map((_, i) => (
          <motion.line
            key={`line-${i}`}
            x1={Math.random() * 400}
            y1={Math.random() * 300}
            x2={Math.random() * 400}
            y2={Math.random() * 300}
            stroke="rgba(255, 255, 255, 0.2)"
            strokeWidth="1"
            animate={{
              opacity: [0.1, 0.4, 0.1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </svg>
    </div>
  )
}

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      <FloatingParticles />
      <NetworkGraph />
      
      {/* Navigation */}
      <nav className="relative z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-2"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-white text-xl font-bold">engram™</span>
          </motion.div>

          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-white/80 hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="text-white/80 hover:text-white transition-colors">Pricing</a>
            <a href="#about" className="text-white/80 hover:text-white transition-colors">About</a>
            <a href="#docs" className="text-white/80 hover:text-white transition-colors">Docs</a>
          </div>

          <div className="flex items-center space-x-4">
            <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
              Sign In
            </Button>
            <Button className="bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600">
              Try for Free →
            </Button>
            <button
              className="md:hidden text-white"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-6 pt-20 pb-32">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mb-6"
            >
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30 px-4 py-2 text-sm font-medium">
                <Sparkles className="w-4 h-4 mr-2" />
                Update: Announcing our $3M fund raise →
              </Badge>
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-5xl md:text-7xl font-bold mb-6 text-white"
            >
              Personalise your AI app with long-term memory API
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-xl md:text-2xl text-white/80 mb-8 max-w-3xl mx-auto leading-relaxed"
            >
              Delight your users with blazing fast and scalable memory for your AI application. Interoperable between models and modalities.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
            >
              <Button size="lg" className="text-lg px-8 py-6 bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600">
                Setup in 5 mins →
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-white/30 text-white hover:bg-white/10">
                Explore Docs
              </Button>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto"
            >
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">10x</div>
                <div className="text-sm text-white/60">Faster than Zep</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-400">25x</div>
                <div className="text-sm text-white/60">Faster than Mem0</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400">70%</div>
                <div className="text-sm text-white/60">Lower cost</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-400">300ms</div>
                <div className="text-sm text-white/60">Recall time</div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Everything you need to remember
            </h2>
            <p className="text-xl text-white/80 max-w-3xl mx-auto">
              Powerful features designed to help you capture, organize, and retrieve your knowledge effortlessly.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
                className="group"
              >
                <Card className="h-full border-0 shadow-2xl hover:shadow-3xl transition-all duration-300 bg-white/5 backdrop-blur-sm border-white/10">
                  <CardHeader>
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                    <CardDescription className="text-base text-white/70">
                      {feature.description}
                    </CardDescription>
                    <Badge variant="secondary" className="w-fit mt-2 bg-white/10 text-white border-white/20">
                      {feature.stats}
                    </Badge>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-6 bg-gradient-to-r from-purple-900/50 to-blue-900/50 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              How it works
            </h2>
            <p className="text-xl text-white/80 max-w-3xl mx-auto">
              Three simple steps to transform your digital life into an intelligent memory system.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="relative">
                  <div className={`w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center text-white text-2xl font-bold`}>
                    {step.number}
                  </div>
                  {index < steps.length - 1 && (
                    <div className="hidden md:block absolute top-10 left-1/2 w-full h-0.5 bg-gradient-to-r from-blue-500 to-purple-600 -z-10" />
                  )}
                </div>
                <div className={`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center`}>
                  <step.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-white">{step.title}</h3>
                <p className="text-white/70 text-lg">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Our customers love us
            </h2>
            <p className="text-xl text-white/80 max-w-3xl mx-auto">
              Builders everywhere are skipping months of infra work and shipping AI products with memory in days.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full border-0 shadow-2xl hover:shadow-3xl transition-all duration-300 bg-white/5 backdrop-blur-sm border-white/10">
                  <CardContent className="p-6">
                    <div className="flex items-center mb-4">
                      <div className="text-4xl mr-3">{testimonial.avatar}</div>
                      <div>
                        <h4 className="font-semibold text-white">{testimonial.name}</h4>
                        <p className="text-sm text-white/60">{testimonial.role}, {testimonial.company}</p>
                      </div>
                    </div>
                    <div className="flex mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                    <p className="text-white/80 italic">"{testimonial.content}"</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 px-6 bg-gradient-to-r from-blue-900/50 to-purple-900/50 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              The fastest memory layer, at a fraction of the cost
            </h2>
            <p className="text-xl text-white/80 max-w-3xl mx-auto">
              Start free, experiment fast, and only pay when your memory becomes your moat. No hidden fees.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
                className="relative"
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="px-4 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                      Most Popular
                    </Badge>
                  </div>
                )}
                <Card className={`h-full border-0 shadow-2xl hover:shadow-3xl transition-all duration-300 ${
                  plan.popular ? 'ring-2 ring-blue-500 bg-white/10' : 'bg-white/5'
                } backdrop-blur-sm border-white/10`}>
                  <CardHeader className="text-center">
                    <CardTitle className="text-2xl text-white">{plan.name}</CardTitle>
                    <div className="flex items-baseline justify-center">
                      <span className="text-4xl font-bold text-white">{plan.price}</span>
                      <span className="text-white/60">{plan.period}</span>
                    </div>
                    <CardDescription className="text-base text-white/70">
                      {plan.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <ul className="space-y-3">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center">
                          <CheckCircle className="w-5 h-5 text-green-400 mr-3" />
                          <span className="text-sm text-white/80">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button 
                      className={`w-full mt-6 ${
                        plan.popular 
                          ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600' 
                          : 'bg-white/10 text-white hover:bg-white/20 border-white/20'
                      }`}
                      size="lg"
                    >
                      {plan.cta}
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Bring your user's context from where they are
            </h2>
            <p className="text-xl text-white/80 max-w-3xl mx-auto">
              Supermemory connects to Google Drive, Notion, Onedrive and more and syncs user context.
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {integrations.map((integration, index) => (
              <motion.div
                key={integration.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05 }}
                className="group"
              >
                <Card className="p-6 text-center hover:shadow-2xl transition-all duration-300 bg-white/5 backdrop-blur-sm border-white/10 border-0">
                  <div className="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">
                    {integration.logo}
                  </div>
                  <h3 className="font-semibold text-sm mb-1 text-white">{integration.name}</h3>
                  <Badge 
                    className={`text-xs ${
                      integration.status === "Connected" 
                        ? 'bg-green-500/20 text-green-400 border-green-500/30' 
                        : 'bg-white/10 text-white/60 border-white/20'
                    }`}
                  >
                    {integration.status}
                  </Badge>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-gradient-to-r from-blue-600 to-purple-600 relative">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Intelligence without memory is just randomness.
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join thousands of users who have transformed their digital life with Engram.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="text-lg px-8 py-6 bg-white text-blue-600 hover:bg-blue-50">
                Start Building Your Memory
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-white text-white hover:bg-white hover:text-blue-600">
                View Pricing
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-2xl font-bold mb-4 text-white">Engram</h3>
              <p className="text-white/60">
                Your AI's memory layer for the modern world.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Product</h4>
              <ul className="space-y-2 text-white/60">
                <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/integrations" className="hover:text-white transition-colors">Integrations</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Resources</h4>
              <ul className="space-y-2 text-white/60">
                <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/support" className="hover:text-white transition-colors">Support</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Company</h4>
              <ul className="space-y-2 text-white/60">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/20 mt-8 pt-8 text-center text-white/60">
            <p>&copy; 2024 Engram. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}