function StatusBanner({ stage }) {
  return (
    <div className="px-5 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-base flex justify-between items-center relative">
      Current Stage: {stage}
      <span className="text-xs font-normal opacity-85 absolute bottom-1.5 right-5">
        Online now
      </span>
    </div>
  );
}

export default StatusBanner;
